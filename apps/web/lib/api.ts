import { loadApiConfig } from "./api-config";
import type { ApiConfig, Profile, Provider, ProviderTestResult, SolveResponse, Subject } from "./types";
import { solveLocally } from "./local-solver";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api/backend";

export async function solveProblem(input: {
  question: string;
  subject: Subject;
  provider: Provider;
  profile: Profile;
  model?: string;
  file?: File | null;
}): Promise<SolveResponse> {
  const apiConfig = loadApiConfig();
  const configuredInput = {
    ...input,
    provider: apiConfig?.provider ?? input.provider,
    model: apiConfig?.model ?? input.model
  };
  const localOnly = process.env.NEXT_PUBLIC_LOCAL_SOLVER === "true";
  if (localOnly) {
    return solveWithBrowserByok(configuredInput, apiConfig);
  }

  const form = new FormData();
  form.set("question", configuredInput.question);
  form.set("subject", configuredInput.subject);
  form.set("provider", configuredInput.provider);
  form.set("profile", input.profile);
  if (configuredInput.model) form.set("model", configuredInput.model);
  if (input.file) form.set("file", input.file);
  if (apiConfig) {
    form.set("apiKey", apiConfig.apiKey);
    form.set("baseUrl", apiConfig.baseUrl);
  }

  const response = await fetch(`${API_URL}/solve`, {
    method: "POST",
    body: form
  }).catch(() => null);

  if (!response || !response.ok) {
    return solveWithBrowserByok(configuredInput, apiConfig);
  }

  try {
    return await response.json();
  } catch {
    return solveWithBrowserByok(configuredInput, apiConfig);
  }
}

export async function testProvider(config: ApiConfig): Promise<ProviderTestResult> {
  const localOnly = process.env.NEXT_PUBLIC_LOCAL_SOLVER === "true";
  if (!localOnly) {
    const response = await fetch(`${API_URL}/provider/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config)
    }).catch(() => null);
    if (response?.ok) return response.json();
  }
  return testProviderInBrowser(config);
}

async function solveWithBrowserByok(
  input: Parameters<typeof solveProblem>[0],
  apiConfig: ApiConfig | null
): Promise<SolveResponse> {
  let effectiveQuestion = input.question;
  const warnings: string[] = [];
  if (input.file && apiConfig?.apiKey) {
    const extracted = await extractProblemTextInBrowser(apiConfig, input.file).catch((error) => {
      warnings.push(`浏览器直连识题失败：${error instanceof Error ? error.message : String(error)}`);
      return "";
    });
    if (extracted) effectiveQuestion = extracted;
  } else if (input.file) {
    warnings.push("已选择文件；请在高级设置中保存自己的 API Key 后启用真实识题。");
  }

  const result = solveLocally({ ...input, question: effectiveQuestion });
  result.provider = apiConfig?.provider ?? result.provider;
  result.model = apiConfig?.model ?? result.model;
  result.model_route.reason_provider = result.provider ?? result.model_route.reason_provider;
  result.model_route.reason_model = result.model ?? result.model_route.reason_model;
  result.model_status = apiConfig?.apiKey && input.file ? "vision_byok_engine_template" : result.model_status;
  result.warnings = [...warnings, ...result.warnings];
  return result;
}

async function testProviderInBrowser(config: ApiConfig): Promise<ProviderTestResult> {
  try {
    if (!config.apiKey) throw new Error("API Key is required");
    if (config.provider === "gemini") {
      await callGeminiText(config, "Reply with OK.");
    } else {
      await callOpenAICompatibleText(config, "Reply with OK.");
    }
    return { success: true, provider: config.provider, model: config.model };
  } catch (error) {
    return {
      success: false,
      provider: config.provider,
      model: config.model,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

async function extractProblemTextInBrowser(config: ApiConfig, file: File): Promise<string> {
  if (config.provider === "deepseek") {
    throw new Error("DeepSeek 不支持直接读取图片或 PDF，请换 OpenAI、Gemini 或支持文件的 Custom API");
  }
  const prompt = "Extract the engineering or math problem text from this file. Return only the problem statement.";
  if (config.provider === "gemini") return callGeminiFileExtraction(config, prompt, file);
  return callOpenAICompatibleFileExtraction(config, prompt, file);
}

async function callOpenAICompatibleText(config: ApiConfig, prompt: string) {
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${config.apiKey}` },
    body: JSON.stringify({ model: config.model, messages: [{ role: "user", content: prompt }], max_tokens: 16 })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function callOpenAICompatibleFileExtraction(config: ApiConfig, prompt: string, file: File): Promise<string> {
  const dataUrl = await fileToDataUrl(file);
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const filePart =
    file.type === "application/pdf"
      ? { type: "file", file: { filename: file.name || "problem.pdf", file_data: dataUrl } }
      : { type: "image_url", image_url: { url: dataUrl } };
  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${config.apiKey}` },
    body: JSON.stringify({
      model: config.model,
      messages: [{ role: "user", content: [{ type: "text", text: prompt }, filePart] }],
      max_tokens: 900,
      temperature: 0.1
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return String(data.choices?.[0]?.message?.content ?? "").trim();
}

async function callGeminiText(config: ApiConfig, prompt: string) {
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const response = await fetch(`${baseUrl}/models/${config.model}:generateContent?key=${encodeURIComponent(config.apiKey)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }] })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function callGeminiFileExtraction(config: ApiConfig, prompt: string, file: File): Promise<string> {
  const base64 = await fileToBase64(file);
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const response = await fetch(`${baseUrl}/models/${config.model}:generateContent?key=${encodeURIComponent(config.apiKey)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }, { inline_data: { mime_type: file.type, data: base64 } }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: 900 }
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  return String(data.candidates?.[0]?.content?.parts?.map((part: { text?: string }) => part.text ?? "").join("\n") ?? "").trim();
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

async function fileToBase64(file: File): Promise<string> {
  const dataUrl = await fileToDataUrl(file);
  return dataUrl.split(",", 2)[1] ?? "";
}
