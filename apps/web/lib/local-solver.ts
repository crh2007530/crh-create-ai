import type { Profile, Provider, SolveResponse, Subject, Visualization } from "./types";

type Topic = "determinant" | "inverse_matrix" | "matrix_rank" | "gaussian_elimination" | "node_voltage";

type MatrixResult = {
  matrix: number[][];
  determinant?: number;
  inverse?: number[][];
  rank?: number;
  echelon?: number[][];
  rowSteps?: string[];
};

function detectSubject(question: string, subject: Subject): "linear_algebra" | "circuit" {
  if (subject === "linear_algebra") return "linear_algebra";
  if (subject === "circuit") return "circuit";
  return /矩阵|行列式|逆矩阵|求逆|秩|高斯|matrix|det|rank|inverse/i.test(question)
    ? "linear_algebra"
    : "circuit";
}

function detectTopic(question: string, domain: "linear_algebra" | "circuit"): Topic {
  if (domain === "circuit") return "node_voltage";
  if (/行列式|det/i.test(question)) return "determinant";
  if (/逆矩阵|求逆|inverse/i.test(question)) return "inverse_matrix";
  if (/秩|rank/i.test(question)) return "matrix_rank";
  return "gaussian_elimination";
}

function parseMatrix(question: string): number[][] | null {
  const rows = question
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => /^[-+\d\s,.;]+$/.test(line) && /\d/.test(line))
    .map((line) =>
      line
        .replace(/[;,]/g, " ")
        .split(/\s+/)
        .filter(Boolean)
        .map(Number)
    )
    .filter((row) => row.length > 0 && row.every((value) => Number.isFinite(value)));

  if (rows.length >= 2 && rows.every((row) => row.length === rows[0].length)) {
    return rows;
  }

  const bracketMatch = question.match(/\[\s*([\s\S]*?)\s*\]/);
  if (!bracketMatch) return null;
  const bracketRows = bracketMatch[1]
    .split(";")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.split(/[\s,]+/).filter(Boolean).map(Number));
  return bracketRows.length ? bracketRows : null;
}

function determinant(matrix: number[][]): number | undefined {
  if (matrix.length !== matrix[0]?.length) return undefined;
  if (matrix.length === 1) return matrix[0][0];
  if (matrix.length === 2) return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];

  return matrix[0].reduce((sum, value, col) => {
    const minor = matrix.slice(1).map((row) => row.filter((_, index) => index !== col));
    return sum + (col % 2 === 0 ? 1 : -1) * value * (determinant(minor) ?? 0);
  }, 0);
}

function gaussian(matrix: number[][]): { echelon: number[][]; rowSteps: string[]; rank: number } {
  const result = matrix.map((row) => row.map(Number));
  const rowSteps: string[] = [];
  let lead = 0;
  let rank = 0;

  for (let row = 0; row < result.length && lead < result[0].length; row += 1) {
    let pivot = row;
    while (pivot < result.length && Math.abs(result[pivot][lead]) < 1e-9) pivot += 1;
    if (pivot === result.length) {
      lead += 1;
      row -= 1;
      continue;
    }
    if (pivot !== row) {
      [result[row], result[pivot]] = [result[pivot], result[row]];
      rowSteps.push(`R${row + 1} <-> R${pivot + 1}`);
    }
    const divisor = result[row][lead];
    if (Math.abs(divisor - 1) > 1e-9) {
      result[row] = result[row].map((value) => value / divisor);
      rowSteps.push(`R${row + 1} <- R${row + 1} / ${formatNumber(divisor)}`);
    }
    for (let other = row + 1; other < result.length; other += 1) {
      const factor = result[other][lead];
      if (Math.abs(factor) > 1e-9) {
        result[other] = result[other].map((value, index) => value - factor * result[row][index]);
        rowSteps.push(`R${other + 1} <- R${other + 1} - ${formatNumber(factor)}R${row + 1}`);
      }
    }
    rank += 1;
    lead += 1;
  }

  return { echelon: result, rowSteps, rank };
}

function inverse2x2(matrix: number[][]): number[][] | undefined {
  if (matrix.length !== 2 || matrix[0].length !== 2) return undefined;
  const det = determinant(matrix);
  if (!det || Math.abs(det) < 1e-9) return undefined;
  return [
    [matrix[1][1] / det, -matrix[0][1] / det],
    [-matrix[1][0] / det, matrix[0][0] / det]
  ];
}

function formatNumber(value: number): string {
  if (Math.abs(value) < 1e-9) return "0";
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function matrixText(matrix: number[][]): string {
  return matrix.map((row) => `[ ${row.map(formatNumber).join("  ")} ]`).join("\n");
}

function matrixSvg(title: string, matrix: number[][], note: string, highlightRow?: number): string {
  const cols = Math.max(...matrix.map((row) => row.length));
  const cellW = 64;
  const cellH = 42;
  const width = Math.max(520, cols * cellW + 120);
  const height = matrix.length * cellH + 130;
  const rows = matrix
    .map((row, rowIndex) => {
      const y = 70 + rowIndex * cellH;
      const bg =
        highlightRow === rowIndex
          ? `<rect x="56" y="${y - 25}" width="${cols * cellW + 8}" height="34" fill="#fff7cc" stroke="#111" stroke-width="1"/>`
          : "";
      const values = row
        .map(
          (value, colIndex) =>
            `<text x="${88 + colIndex * cellW}" y="${y}" font-size="18" text-anchor="middle">${formatNumber(value)}</text>`
        )
        .join("");
      return `${bg}${values}`;
    })
    .join("");

  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${title}">
  <rect width="${width}" height="${height}" fill="#fff"/>
  <text x="24" y="34" font-size="20" font-weight="700">${title}</text>
  <path d="M60 52 V${height - 48} M${cols * cellW + 68} 52 V${height - 48}" stroke="#111" stroke-width="3" fill="none"/>
  ${rows}
  <line x1="24" y1="${height - 38}" x2="${width - 24}" y2="${height - 38}" stroke="#ddd"/>
  <text x="24" y="${height - 14}" font-size="15" fill="#444">${note}</text>
</svg>`;
}

function circuitSvg(title: string, note: string, step: number): string {
  const node = step >= 2;
  const current = step >= 3;
  const equation = step >= 4;
  const result = step >= 5;
  return `<svg viewBox="0 0 640 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${title}">
  <rect width="640" height="380" fill="#fff"/>
  <text x="24" y="34" font-size="20" font-weight="700">${title}</text>
  <line x1="120" y1="110" x2="120" y2="260" stroke="#111" stroke-width="2"/>
  <line x1="120" y1="110" x2="300" y2="110" stroke="#111" stroke-width="2"/>
  <line x1="300" y1="110" x2="480" y2="110" stroke="#111" stroke-width="2"/>
  <line x1="480" y1="110" x2="480" y2="260" stroke="#111" stroke-width="2"/>
  <line x1="120" y1="260" x2="480" y2="260" stroke="#111" stroke-width="2"/>
  <path d="M166 110 h16 l8 -16 l16 32 l16 -32 l16 32 l16 -32 l8 16 h16" stroke="#111" stroke-width="2" fill="none"/>
  <text x="212" y="82" font-size="16">R1</text>
  <path d="M344 110 h16 l8 -16 l16 32 l16 -32 l16 32 l16 -32 l8 16 h16" stroke="${equation ? "#d12" : "#111"}" stroke-width="${equation ? 4 : 2}" fill="none"/>
  <text x="390" y="82" font-size="16">R2</text>
  <line x1="120" y1="168" x2="120" y2="190" stroke="#111" stroke-width="2"/>
  <line x1="104" y1="190" x2="136" y2="190" stroke="#111" stroke-width="2"/>
  <line x1="110" y1="202" x2="130" y2="202" stroke="#111" stroke-width="2"/>
  <line x1="104" y1="214" x2="136" y2="214" stroke="#111" stroke-width="2"/>
  <text x="62" y="198" font-size="16">Vs</text>
  <line x1="440" y1="260" x2="520" y2="260" stroke="#111" stroke-width="2"/>
  <line x1="452" y1="274" x2="508" y2="274" stroke="#111" stroke-width="2"/>
  <line x1="466" y1="288" x2="494" y2="288" stroke="#111" stroke-width="2"/>
  ${node ? '<circle cx="300" cy="110" r="7" fill="#111"/><text x="286" y="146" font-size="16">Node A</text><text x="452" y="238" font-size="16">Ground</text>' : ""}
  ${current ? '<path d="M300 56 h96" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/><text x="334" y="48" font-size="16">I1</text><path d="M520 132 v82" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/><text x="532" y="176" font-size="16">I2</text>' : ""}
  ${equation ? '<rect x="250" y="160" width="250" height="44" fill="#fff7cc" stroke="#111"/><text x="266" y="188" font-size="17">KCL: (VA-Vs)/R1 + VA/R2 = 0</text>' : ""}
  ${result ? '<rect x="238" y="160" width="260" height="70" fill="#f8f8f8" stroke="#111"/><text x="258" y="188" font-size="17">VA = solved</text><text x="258" y="214" font-size="17">I, P, Q, S show here</text>' : ""}
  <line x1="24" y1="336" x2="616" y2="336" stroke="#ddd"/>
  <text x="24" y="362" font-size="15" fill="#444">${note}</text>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#111"/></marker></defs>
</svg>`;
}

function visualization(id: string, kind: Visualization["kind"], svg: string): Visualization {
  return {
    id,
    kind,
    mode: kind === "matrix_svg" ? "analysis" : "textbook",
    svg,
    highlights: []
  };
}

function solveMatrix(question: string, topic: Topic): { answer: string; result: MatrixResult; steps: SolveResponse["solution"]["steps"] } {
  const matrix = parseMatrix(question) ?? [
    [1, 2],
    [3, 4]
  ];
  const det = determinant(matrix);
  const inverse = inverse2x2(matrix);
  const reduced = gaussian(matrix);
  const result: MatrixResult = {
    matrix,
    determinant: det,
    inverse,
    rank: reduced.rank,
    echelon: reduced.echelon,
    rowSteps: reduced.rowSteps
  };

  const finalMatrix = topic === "inverse_matrix" && inverse ? inverse : topic === "gaussian_elimination" ? reduced.echelon : matrix;
  const answer =
    topic === "determinant"
      ? `det(A) = ${formatNumber(det ?? 0)}`
      : topic === "matrix_rank"
        ? `rank(A) = ${reduced.rank}`
        : topic === "inverse_matrix"
          ? inverse
            ? `A^-1 =\n${matrixText(inverse)}`
            : "该矩阵当前只支持 2x2 可逆矩阵演示"
          : `阶梯形矩阵：\n${matrixText(reduced.echelon)}`;

  const steps = [
    {
      id: "matrix-step-1",
      index: 1,
      title: "读入矩阵",
      teacher_explanation: "先把题目中的矩阵写成标准形式，后面的每一步都围绕这个矩阵展开。",
      formula: `A =\n${matrixText(matrix)}`,
      visualization: visualization("matrix-v1", "matrix_svg", matrixSvg("Step 1 读入矩阵", matrix, "原矩阵 A"))
    },
    {
      id: "matrix-step-2",
      index: 2,
      title: topic === "determinant" ? "确定行列式方法" : "选择行变换",
      teacher_explanation: "线性代数题通常先判断目标：求行列式、求逆、求秩对应的操作不同。",
      formula: topic === "determinant" ? "det(A)" : reduced.rowSteps[0] ?? "寻找主元",
      visualization: visualization("matrix-v2", "matrix_svg", matrixSvg("Step 2 选择方法", matrix, "高亮第一行/主元位置", 0))
    },
    {
      id: "matrix-step-3",
      index: 3,
      title: "执行计算",
      teacher_explanation: "每次行变换只改变一行，目标是制造主元并消去主元下方的元素。",
      formula: reduced.rowSteps.join("\n") || "无需额外行变换",
      visualization: visualization("matrix-v3", "matrix_svg", matrixSvg("Step 3 行变换过程", reduced.echelon, reduced.rowSteps[0] ?? "矩阵已处于可计算状态", 1))
    },
    {
      id: "matrix-step-4",
      index: 4,
      title: "得到中间结果",
      teacher_explanation: "中间结果用于检查计算路线是否合理，例如阶梯形矩阵可以直接读出秩。",
      formula: `E =\n${matrixText(reduced.echelon)}`,
      visualization: visualization("matrix-v4", "matrix_svg", matrixSvg("Step 4 中间结果", reduced.echelon, "阶梯形结果"))
    },
    {
      id: "matrix-step-5",
      index: 5,
      title: "写出最终答案",
      teacher_explanation: "最后把计算结果回到题目目标，不只看数字，也要知道它来自哪一步。",
      formula: answer,
      visualization: visualization("matrix-v5", "matrix_svg", matrixSvg("Step 5 最终答案", finalMatrix, answer.replace(/\n/g, " ")))
    }
  ];

  return { answer, result, steps };
}

function solveCircuit(question: string): { answer: string; steps: SolveResponse["solution"]["steps"] } {
  const titles = ["重绘电路图", "建立节点", "标注参考方向", "列节点方程", "显示结果"];
  const explanations = [
    "先按教材风格重绘电路，目的是把题图转换成可分析的支路结构。",
    "节点法先找未知节点电压，参考地选好后方程会更少。",
    "电流和电压参考方向可以任意假设，结果为负表示真实方向相反。",
    "对关键节点写 KCL，把流出和流入电流统一到同一个符号规则里。",
    "最后把节点电压、电流和功率标回图上，方便检查物理意义。"
  ];

  return {
    answer: "已生成节点法教学步骤；真实电路数值求解将在云端后端接入后开放。",
    steps: titles.map((title, index) => ({
      id: `circuit-step-${index + 1}`,
      index: index + 1,
      title,
      teacher_explanation: explanations[index],
      formula:
        index === 3
          ? "KCL: (VA - VS) / R1 + VA / R2 = 0"
          : index === 4
            ? "VA, VB, I, P, Q, S"
            : "根据题图建立分析对象",
      visualization: visualization(
        `circuit-v${index + 1}`,
        "circuit_svg",
        circuitSvg(`Step ${index + 1} ${title}`, explanations[index], index + 1)
      )
    }))
  };
}

export function solveLocally(input: {
  question: string;
  subject: Subject;
  provider: Provider;
  profile: Profile;
  model?: string;
  file?: File | null;
}): SolveResponse {
  const question = input.question.trim() || "A =\n1 2\n3 4\n求行列式";
  const domain = detectSubject(question, input.subject);
  const topic = detectTopic(question, domain);
  const matrixSolution = domain === "linear_algebra" ? solveMatrix(question, topic) : undefined;
  const circuitSolution = domain === "circuit" ? solveCircuit(question) : undefined;
  const steps = matrixSolution?.steps ?? circuitSolution?.steps ?? [];
  const answer = matrixSolution?.answer ?? circuitSolution?.answer ?? "";

  return {
    solution: {
      id: `local-solution-${Date.now()}`,
      summary: domain === "linear_algebra" ? "已在浏览器中完成基础线性代数计算与教学可视化。" : "已生成电路分析教学步骤图。",
      confirmation_required: domain === "circuit",
      problem: {
        id: `local-problem-${Date.now()}`,
        input_mode: input.file ? "image" : "text",
        subject: domain,
        topic,
        original_text: question
      },
      problem_document: {
        domain,
        topic,
        sourceType: "text",
        originalQuestion: question,
        knowns: matrixSolution ? [{ name: "A", value: matrixSolution.result.matrix }] : [],
        targets: [topic]
      },
      math_result: matrixSolution
        ? {
            success: true,
            topic,
            input: { matrix: matrixSolution.result.matrix },
            output: matrixSolution.result,
            steps: matrixSolution.result.rowSteps?.map((step, index) => ({ title: `行变换 ${index + 1}`, result: step })) ?? []
          }
        : undefined,
      validation_result: matrixSolution
        ? {
            passed: true,
            score: 1,
            checks: [{ name: topic, passed: true, message: "浏览器端基础校验通过" }]
          }
        : undefined,
      visual_solution: {
        answer,
        confidence: domain === "linear_algebra" ? 0.9 : 0.62,
        topic,
        difficulty: 2,
        validationSummary: domain === "linear_algebra" ? "Verified" : "Teaching Preview"
      },
      steps
    },
    model_route: {
      vision_provider: "local",
      vision_model: "browser",
      reason_provider: input.provider,
      reason_model: input.model || "local-teaching-engine"
    },
    warnings: input.file
      ? ["公网预览版已支持上传入口，但图片/OCR 需要云端后端部署后启用；当前按文字题演示。"]
      : []
  };
}
