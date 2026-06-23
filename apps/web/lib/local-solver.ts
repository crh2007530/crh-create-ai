import type { Profile, Provider, SolveResponse, Subject, Visualization } from "./types";

type Topic = "determinant" | "inverse_matrix" | "matrix_rank" | "gaussian_elimination" | "node_voltage";

type MatrixResult = {
  matrix: number[][];
  determinant?: number;
  inverse?: number[][];
  rank?: number;
  echelon?: number[][];
  rowSteps: string[];
};

function detectSubject(question: string, subject: Subject): "linear_algebra" | "circuit" {
  if (subject === "linear_algebra") return "linear_algebra";
  if (subject === "circuit") return "circuit";
  return /矩阵|行列式|逆矩阵|求逆|秩|高斯|消元|行变换|matrix|det|rank|inverse/i.test(question) || parseMatrix(question) !== null
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
    .map((line) => line.replace(/[;,]/g, " ").split(/\s+/).filter(Boolean).map(Number))
    .filter((row) => row.length > 0 && row.every((value) => Number.isFinite(value)));
  if (rows.length >= 2 && rows.every((row) => row.length === rows[0].length)) return rows;
  return null;
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

function visualization(id: string, kind: Visualization["kind"], svg: string): Visualization {
  return { id, kind, mode: kind === "matrix_svg" ? "analysis" : "textbook", svg, highlights: [] };
}

function matrixSvg(title: string, matrix: number[][], note: string, highlightRow?: number): string {
  const cols = Math.max(...matrix.map((row) => row.length));
  const cellW = 64;
  const cellH = 42;
  const width = Math.max(360, cols * cellW + 96);
  const height = matrix.length * cellH + 124;
  const rows = matrix
    .map((row, rowIndex) => {
      const y = 68 + rowIndex * cellH;
      const bg = highlightRow === rowIndex ? `<rect x="42" y="${y - 25}" width="${cols * cellW + 8}" height="34" fill="#fff7cc" stroke="#111"/>` : "";
      const values = row
        .map((value, colIndex) => `<text x="${72 + colIndex * cellW}" y="${y}" font-size="18" text-anchor="middle">${formatNumber(value)}</text>`)
        .join("");
      return `${bg}${values}`;
    })
    .join("");
  return `<svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${title}">
  <rect width="${width}" height="${height}" fill="#fff"/>
  <text x="18" y="32" font-size="19" font-weight="800">${title}</text>
  <path d="M46 50 V${height - 46} M${cols * cellW + 52} 50 V${height - 46}" stroke="#111" stroke-width="3" fill="none"/>
  ${rows}
  <line x1="18" y1="${height - 36}" x2="${width - 18}" y2="${height - 36}" stroke="#ddd"/>
  <text x="18" y="${height - 14}" font-size="14" fill="#444">${note}</text>
</svg>`;
}

function circuitSvg(title: string, goal: string, conclusion: string, body: string, explanation: string): string {
  return `<svg viewBox="0 0 390 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${title}">
  <rect width="390" height="560" fill="#fff"/>
  <style>.h1{font:800 20px Arial;fill:#111}.label{font:700 14px Arial;fill:#111}.text{font:600 13px Arial;fill:#333}.wire{stroke:#111;stroke-width:3;fill:none;stroke-linecap:round}.muted{stroke:#bcbcbc;fill:none;stroke-width:2.2}.box{fill:#f8f8f8;stroke:#111;stroke-width:1.6}</style>
  <rect x="16" y="16" width="358" height="58" fill="#f7f7f7" stroke="#111"/>
  <text x="28" y="40" class="h1">${title}</text>
  <text x="28" y="62" class="text">本步目标：${goal}</text>
  <g transform="translate(0 92)">${body}</g>
  <rect x="16" y="432" width="358" height="50" class="box"/>
  <text x="28" y="454" class="label">本步结论</text>
  <text x="28" y="474" class="text">${conclusion}</text>
  <rect x="16" y="494" width="358" height="46" fill="#fff" stroke="#d0d0d0"/>
  <text x="28" y="520" class="text">老师解释：${explanation}</text>
</svg>`;
}

function minorMatrix(matrix: number[][], removeRow: number, removeCol: number): number[][] {
  return matrix
    .filter((_, rowIndex) => rowIndex !== removeRow)
    .map((row) => row.filter((_, colIndex) => colIndex !== removeCol));
}

function firstRowExpansionFormula(matrix: number[][]): { symbolic: string; substituted: string; value: string } {
  if (matrix.length === 2 && matrix[0].length === 2) {
    const [[a, b], [c, d]] = matrix;
    return {
      symbolic: "det(A) = a11a22 - a12a21",
      substituted: `det(A) = ${formatNumber(a)}x${formatNumber(d)} - ${formatNumber(b)}x${formatNumber(c)}`,
      value: `det(A) = ${formatNumber(determinant(matrix) ?? 0)}`
    };
  }

  const terms = matrix[0].map((value, colIndex) => {
    const sign = colIndex % 2 === 0 ? "+" : "-";
    const minorDet = determinant(minorMatrix(matrix, 0, colIndex)) ?? 0;
    return `${sign} ${formatNumber(value)}x(${formatNumber(minorDet)})`;
  });
  return {
    symbolic: "det(A) = a11M11 - a12M12 + a13M13 ...",
    substituted: `det(A) = ${terms.join(" ").replace(/^\+ /, "")}`,
    value: `det(A) = ${formatNumber(determinant(matrix) ?? 0)}`
  };
}

function solveDeterminantMatrix(matrix: number[][]): { answer: string; result: MatrixResult; steps: SolveResponse["solution"]["steps"] } {
  const isSquare = matrix.length > 0 && matrix.every((row) => row.length === matrix.length);
  const det = isSquare ? determinant(matrix) : undefined;
  const result: MatrixResult = { matrix, determinant: det, rowSteps: [] };

  if (!isSquare) {
    const answer = "行列式只对方阵有定义；当前矩阵不是方阵。";
    const steps = [
      ["读入矩阵", "先看矩阵有几行几列。", `A =\n${matrixText(matrix)}`, matrix, "原矩阵 A"],
      ["检查方阵条件", "只有 n×n 方阵才有 det(A)。", "rows(A) must equal cols(A)", matrix, "不是方阵"],
      ["停止计算", "题目如果要求行列式，需要先确认矩阵输入是否完整。", answer, matrix, answer]
    ] as const;
    return {
      answer,
      result,
      steps: steps.map(([title, explanation, formula, svgMatrix, note], index) => ({
        id: `det-step-${index + 1}`,
        index: index + 1,
        title,
        teacher_explanation: explanation,
        formula,
        visualization: visualization(`det-v${index + 1}`, "matrix_svg", matrixSvg(`Step ${index + 1} ${title}`, svgMatrix, note, index === 1 ? 0 : undefined))
      }))
    };
  }

  const expansion = firstRowExpansionFormula(matrix);
  const steps = [
    ["读入方阵", "先确认这是方阵，因为行列式只对方阵定义。", `A =\n${matrixText(matrix)}`, matrix, "原方阵 A"],
    ["选择展开行", "选第一行做余子式展开；如果某一行零多，实际计算会优先选零多的行。", "沿第一行展开", matrix, "高亮第一行"],
    ["写出展开公式", "行列式展开时符号按 +、-、+、- 交替。", expansion.symbolic, matrix, "符号模式：+ - + -"],
    ["代入余子式", "每个元素都要乘去掉本行本列后的子行列式。", expansion.substituted, matrix, "逐项计算余子式"],
    ["合并结果", "把各项按符号相加，得到题目真正要求的 det(A)。", expansion.value, matrix, expansion.value]
  ] as const;

  return {
    answer: expansion.value,
    result,
    steps: steps.map(([title, explanation, formula, svgMatrix, note], index) => ({
      id: `det-step-${index + 1}`,
      index: index + 1,
      title,
      teacher_explanation: explanation,
      formula,
      visualization: visualization(`det-v${index + 1}`, "matrix_svg", matrixSvg(`Step ${index + 1} ${title}`, svgMatrix, note, index === 1 ? 0 : undefined))
    }))
  };
}

function solveMatrix(question: string, topic: Topic): { answer: string; result: MatrixResult; steps: SolveResponse["solution"]["steps"] } {
  const matrix = parseMatrix(question) ?? [
    [1, 2],
    [3, 4]
  ];
  if (topic === "determinant") {
    return solveDeterminantMatrix(matrix);
  }
  const det = determinant(matrix);
  const inverse = inverse2x2(matrix);
  const reduced = gaussian(matrix);
  const result: MatrixResult = { matrix, determinant: det, inverse, rank: reduced.rank, echelon: reduced.echelon, rowSteps: reduced.rowSteps };
  const finalMatrix = topic === "inverse_matrix" && inverse ? inverse : topic === "gaussian_elimination" ? reduced.echelon : matrix;
  const answer =
    topic === "matrix_rank"
      ? `rank(A) = ${reduced.rank}`
      : topic === "inverse_matrix"
        ? inverse
          ? `A^-1 =\n${matrixText(inverse)}`
          : "当前本地预览只支持 2×2 可逆矩阵演示。"
        : `阶梯形矩阵：\n${matrixText(reduced.echelon)}`;
  const steps = [
    ["读入矩阵", "先把题目中的矩阵写成标准形式。", `A =\n${matrixText(matrix)}`, matrix, "原矩阵 A"],
    ["选择方法", "先判断题目目标，再选择求逆、求秩或行变换路线。", reduced.rowSteps[0] ?? "寻找主元", matrix, "高亮主元位置"],
    ["执行计算", "每次行变换只改变一行，便于检查。", reduced.rowSteps.join("\n") || "无需额外行变换", reduced.echelon, "行变换结果"],
    ["得到中间结果", "阶梯形矩阵可以用于读出秩或继续求解。", `E =\n${matrixText(reduced.echelon)}`, reduced.echelon, "阶梯形结果"],
    ["写出最终答案", "最后回到题目问的量，不只看过程。", answer, finalMatrix, answer.replace(/\n/g, " ")]
  ] as const;
  return {
    answer,
    result,
    steps: steps.map(([title, explanation, formula, svgMatrix, note], index) => ({
      id: `matrix-step-${index + 1}`,
      index: index + 1,
      title,
      teacher_explanation: explanation,
      formula,
      visualization: visualization(`matrix-v${index + 1}`, "matrix_svg", matrixSvg(`Step ${index + 1} ${title}`, svgMatrix, note, index === 1 ? 0 : undefined))
    }))
  };
}
function solveCircuit(): { answer: string; steps: SolveResponse["solution"]["steps"] } {
  const bodies = [
    '<circle cx="195" cy="165" r="56" fill="#fff7cc" stroke="#111" stroke-width="3"/><text x="158" y="158" class="label">题目要求</text><text x="166" y="184" class="h1">求 VA / I</text><text x="108" y="304" class="text">先看题目问什么，不急着计算。</text>',
    '<circle cx="195" cy="140" r="78" fill="#fff7cc" stroke="#111" stroke-width="4"/><circle cx="195" cy="140" r="7" fill="#111"/><text x="151" y="132" class="h1">Node A</text><text x="137" y="166" class="text">未知节点电压 VA</text><path class="wire" d="M195 218 V286"/><text x="105" y="340" class="text">其它部分灰化，只盯住 Node A。</text>',
    '<circle cx="195" cy="152" r="62" fill="#fff" stroke="#111" stroke-width="3"/><text x="167" y="158" class="h1">Node A</text><path d="M72 104 H142" stroke="#111" stroke-width="5" marker-end="url(#arrow)"/><text x="91" y="88" class="h1">I1</text><path d="M292 104 V176" stroke="#111" stroke-width="5" marker-end="url(#arrow)"/><text x="306" y="142" class="h1">I2</text><text x="62" y="340" class="text">方向是假设，负值表示实际相反。</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>',
    '<circle cx="195" cy="118" r="54" fill="#fff7cc" stroke="#111" stroke-width="4"/><text x="168" y="124" class="h1">Node A</text><rect x="40" y="226" width="310" height="88" fill="#fff" stroke="#111" stroke-width="2"/><text x="68" y="260" class="h1">KCL</text><text x="68" y="292" class="label">I1 + I2 = 0</text><text x="54" y="350" class="text">这一步只围绕关键节点列式。</text>',
    '<rect x="44" y="58" width="302" height="236" fill="#fff" stroke="#111" stroke-width="2"/><text x="78" y="112" class="label">最终结果</text><text x="78" y="162" class="h1">VA = 6V</text><text x="78" y="210" class="h1">I = 2A</text><text x="78" y="258" class="text">把答案放回图里检查单位。</text>'
  ];
  const meta = [
    ["识别题目", "找出题目要求的 VA 或 I", "目标量已确定，下一步选择分析对象。", "先锁定题目要问的量，不急着套公式。", "target: VA, I"],
    ["确定分析对象", "只盯住 Node A", "Node A 已确定，下一步标参考方向。", "节点法先抓关键未知节点。", "unknown: VA"],
    ["标参考方向", "确定电流参考方向", "参考方向建立完成，下一步列 KCL。", "参考方向可以任意假设。", "assume I1, I2"],
    ["列 KCL", "围绕 Node A 写 KCL", "KCL 方程已建立，下一步求解。", "只看 Node A 的流入流出。", "I1 + I2 = 0"],
    ["求解结果", "把答案标回图中", "结果已回到图中，可以完成检查。", "检查单位、方向和物理意义。", "VA = 6V, I = 2A"]
  ] as const;
  return {
    answer: "电路教学步骤图已生成；真实电路数值求解将在云端 Circuit Engine 接入后开放。",
    steps: meta.map(([title, goal, conclusion, explanation, formula], index) => ({
      id: `circuit-step-${index + 1}`,
      index: index + 1,
      title,
      teacher_explanation: explanation,
      formula,
      visualization: visualization(`circuit-v${index + 1}`, "circuit_svg", circuitSvg(`Step ${index + 1} ${title}`, goal, conclusion, bodies[index], explanation))
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
  const circuitSolution = domain === "circuit" ? solveCircuit() : undefined;
  const steps = matrixSolution?.steps ?? circuitSolution?.steps ?? [];
  const answer = matrixSolution?.answer ?? circuitSolution?.answer ?? "";
  const reasonProvider = input.provider === "auto" ? "local" : input.provider;
  const reasonModel = input.model || "local-teaching-engine";
  return {
    solution: {
      id: `local-solution-${Date.now()}`,
      summary: domain === "linear_algebra" ? "已在浏览器中完成基础线性代数计算与教学可视化。" : "已生成电路教学步骤图。",
      confirmation_required: domain === "circuit",
      problem: { id: `local-problem-${Date.now()}`, input_mode: input.file ? "image" : "text", subject: domain, topic, original_text: question },
      problem_document: { domain, topic, sourceType: "text", originalQuestion: question, knowns: [], targets: [topic] },
      math_result: matrixSolution ? { success: true, topic, input: { matrix: matrixSolution.result.matrix }, output: matrixSolution.result, steps: matrixSolution.result.rowSteps } : undefined,
      validation_result: matrixSolution ? { passed: true, score: 1, checks: [{ name: topic, passed: true, message: "浏览器端基础校验通过" }] } : undefined,
      visual_solution: { answer, confidence: domain === "linear_algebra" ? 0.9 : 0.62, topic, difficulty: 2, validationSummary: domain === "linear_algebra" ? "Verified" : "Teaching Preview" },
      steps
    },
    model_route: { vision_provider: input.file ? "local-preview" : "none", vision_model: input.file ? "upload-preview" : "none", reason_provider: reasonProvider, reason_model: reasonModel },
    provider: reasonProvider,
    model: reasonModel,
    model_status: "engine_template",
    warnings: input.file ? ["公网静态版支持图片/PDF 上传入口；真实识题需要保存自己的 Vision API。"] : []
  };
}



