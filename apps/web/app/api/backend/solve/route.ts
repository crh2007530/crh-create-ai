import { solveLocally } from "@/lib/local-solver";
import type { Provider, Subject } from "@/lib/types";

export const runtime = "nodejs";

const DEFAULT_BASE_URL = "https://ai-pixel.online";
const DEFAULT_MODEL = "gpt-4o-mini";

export async function POST(request: Request) {
  const form = await request.formData();
  const question = String(form.get("question") ?? "");
  const subject = (String(form.get("subject") || "linear_algebra") as Subject) || "linear_algebra";
  const provider = (String(form.get("provider") || "auto") as Provider) || "auto";
  const model = String(form.get("model") || process.env.CUSTOM_MODEL || DEFAULT_MODEL);
  const file = form.get("file");

  let effectiveQuestion = question.trim();
  let extractedText = "";
  const warnings: string[] = [];

  if (file instanceof File && file.size > 0) {
    extractedText = await extractProblemText(file, model);
    effectiveQuestion = extractedText.trim();
    if (!effectiveQuestion) {
      return Response.json(
        { error: "图片识别没有读出有效题目，请换一张更清晰的图片。" },
        { status: 422 }
      );
    }
  }

  const result = solveLocally({
    question: effectiveQuestion,
    subject,
    provider,
    profile: "auto",
    model,
    file: file instanceof File ? file : null
  });

  result.provider = "platform";
  result.model = model;
  result.model_route.reason_provider = "platform";
  result.model_route.reason_model = model;
  if (extractedText) {
    result.extracted_text = extractedText;
    result.model_route.vision_provider = "platform";
    result.model_route.vision_model = model;
    result.model_status = "platform_vision_local_teaching";
    result.warnings = ["已完成拍照识题，并生成线代教学可视化。", ...warnings];
  }
  return Response.json(result);
}

async function extractProblemText(file: File, model: string): Promise<string> {
  const apiKey = process.env.CUSTOM_API_KEY;
  if (!apiKey) {
    throw new Error("服务器未配置 CUSTOM_API_KEY，拍照识题暂不可用。");
  }

  const baseUrl = (process.env.CUSTOM_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
  const dataUrl = await fileToDataUrl(file);
  const filePart =
    file.type === "application/pdf"
      ? { type: "file", file: { filename: file.name || "problem.pdf", file_data: dataUrl } }
      : { type: "image_url", image_url: { url: dataUrl } };
  const prompt = [
    "你是线性代数题目识别器，只从图片中提取题目文字，不要解题。",
    "必须保留矩阵的行列结构。例如：A =\\n1 2\\n3 4\\n求行列式。",
    "如果题目要求行列式、逆矩阵、秩、高斯消元、特征值，请保留这些关键词。",
    "只返回题目文本，不要返回步骤、解释或答案。"
  ].join("\n");

  const response = await fetch(`${baseUrl}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: [{ type: "text", text: prompt }, filePart] }],
      temperature: 0.1,
      max_tokens: 900
    })
  });

  if (!response.ok) {
    const message = await response.text().catch(() => "");
    throw new Error(`平台识题服务失败：HTTP ${response.status} ${message.slice(0, 200)}`);
  }
  const data = await response.json();
  return normalizeText(String(data.choices?.[0]?.message?.content ?? ""));
}

async function fileToDataUrl(file: File): Promise<string> {
  const buffer = Buffer.from(await file.arrayBuffer());
  return `data:${file.type || "image/png"};base64,${buffer.toString("base64")}`;
}

function normalizeText(text: string): string {
  return text
    .replace(/^```[a-zA-Z]*\s*/g, "")
    .replace(/```$/g, "")
    .replace(/^(题目文本|识别结果|Problem)\s*[:：]\s*/i, "")
    .trim();
}
