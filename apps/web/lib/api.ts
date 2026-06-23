import { loadApiConfig } from "./api-config";
import { solveLocally } from "./local-solver";
import type { ApiConfig, Profile, Provider, ProviderTestResult, SolveResponse, Subject, TeacherAskResult } from "./types";

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
  if (!localOnly) {
    const serverResult = await solveWithServer(configuredInput, apiConfig);
    if (serverResult) return serverResult;
  }

  if (input.file) {
    throw new Error("拍照识题需要连接平台代理后端。文字题可直接输入后生成可视化；要让普通用户拍照即用，请先部署 FastAPI 后端并配置 CUSTOM_API_KEY。");
  }
  return solveLocally(configuredInput);
}

async function solveWithServer(
  input: Parameters<typeof solveProblem>[0],
  apiConfig: ApiConfig | null
): Promise<SolveResponse | null> {
  const form = new FormData();
  form.set("question", input.question);
  form.set("subject", input.subject);
  form.set("provider", apiConfig?.provider ?? input.provider);
  form.set("profile", input.profile);
  if (apiConfig?.model ?? input.model) form.set("model", apiConfig?.model ?? input.model ?? "");
  if (input.file) form.set("file", input.file);
  if (apiConfig) {
    form.set("apiKey", apiConfig.apiKey);
    form.set("baseUrl", apiConfig.baseUrl);
  }

  const response = await fetch(`${API_URL}/solve`, { method: "POST", body: form }).catch(() => null);
  if (!response) return null;
  if (!response.ok) {
    const message = await response.text().catch(() => "");
    throw new Error(`平台识题服务返回错误：HTTP ${response.status}${message ? ` ${message.slice(0, 180)}` : ""}`);
  }
  return response.json();
}

export async function testProvider(config: ApiConfig): Promise<ProviderTestResult> {
  const response = await fetch(`${API_URL}/provider/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config)
  }).catch(() => null);
  if (response?.ok) return response.json();
  return testProviderInBrowser(config);
}

export async function askTeacher(input: {
  question: string;
  response?: SolveResponse;
  activeStepIndex?: number;
}): Promise<TeacherAskResult> {
  const apiConfig = loadApiConfig();
  if (!apiConfig?.apiKey) return answerWithLocalTeacher(input.question, input.response, input.activeStepIndex);

  const prompt = buildTeacherPrompt(input.question, input.response, input.activeStepIndex);
  try {
    const answer =
      apiConfig.provider === "gemini"
        ? await callGeminiTextAnswer(apiConfig, prompt, 700)
        : await callOpenAICompatibleTextAnswer(apiConfig, prompt, 700);
    return {
      answer: answer || "我看到了你的问题，但模型没有返回有效内容。你可以换一种问法再试一次。",
      provider: apiConfig.provider,
      model: apiConfig.model,
      mode: "ai"
    };
  } catch (error) {
    const local = answerWithLocalTeacher(input.question, input.response, input.activeStepIndex);
    return {
      ...local,
      error: `AI 调用失败，已切换本地回答：${error instanceof Error ? error.message : String(error)}`
    };
  }
}

async function testProviderInBrowser(config: ApiConfig): Promise<ProviderTestResult> {
  try {
    if (!config.apiKey) throw new Error("API Key 不能为空");
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

async function callOpenAICompatibleText(config: ApiConfig, prompt: string, maxTokens = 16) {
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${config.apiKey}` },
    body: JSON.stringify({ model: config.model, messages: [{ role: "user", content: prompt }], max_tokens: maxTokens, temperature: 0.2 })
  });
  if (!response.ok) throw new Error(await responseError(response));
  return response.json();
}

async function callOpenAICompatibleTextAnswer(config: ApiConfig, prompt: string, maxTokens: number): Promise<string> {
  const data = await callOpenAICompatibleText(config, prompt, maxTokens);
  return String(data.choices?.[0]?.message?.content ?? "").trim();
}

async function callGeminiText(config: ApiConfig, prompt: string, maxTokens = 16) {
  const baseUrl = config.baseUrl.replace(/\/$/, "");
  const response = await fetch(`${baseUrl}/models/${config.model}:generateContent?key=${encodeURIComponent(config.apiKey)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.2, maxOutputTokens: maxTokens }
    })
  });
  if (!response.ok) throw new Error(await responseError(response));
  return response.json();
}

async function callGeminiTextAnswer(config: ApiConfig, prompt: string, maxTokens: number): Promise<string> {
  const data = await callGeminiText(config, prompt, maxTokens);
  return String(data.candidates?.[0]?.content?.parts?.map((part: { text?: string }) => part.text ?? "").join("\n") ?? "").trim();
}

function buildTeacherPrompt(question: string, response?: SolveResponse, activeStepIndex = 0): string {
  const solution = response?.solution;
  const activeStep = solution?.steps?.[activeStepIndex];
  const stepSummary = solution?.steps
    ?.map((step) => `Step ${step.index}: ${step.title}\n公式: ${step.formula}\n解释: ${step.teacher_explanation}`)
    .join("\n\n");
  return [
    "你是 crh create AI 的工科老师。请用中文回答学生追问。",
    "要求：最多 4 句话，优先解释为什么这样做；不要长篇聊天；必要时引用步骤编号。",
    `学生追问：${question}`,
    solution ? `原题：${solution.problem.original_text}` : "",
    solution?.visual_solution?.answer ? `当前答案：${solution.visual_solution.answer}` : "",
    activeStep ? `当前展开步骤：Step ${activeStep.index} ${activeStep.title}` : "",
    stepSummary ? `已有步骤：\n${stepSummary}` : ""
  ]
    .filter(Boolean)
    .join("\n\n");
}

function answerWithLocalTeacher(question: string, response?: SolveResponse, activeStepIndex = 0): TeacherAskResult {
  const normalized = question.toLowerCase();
  const solution = response?.solution;
  const activeStep = solution?.steps?.[activeStepIndex] ?? solution?.steps?.[0];
  let answer = "当前没有接入 AI，我先用本地教学引擎回答：";

  if (!solution) {
    answer += "你可以先输入题目文本。拍照识题需要平台后端代理连接。";
  } else if (/为什么|why|原因|怎么/.test(question)) {
    answer += activeStep
      ? `这一部的核心是：${activeStep.teacher_explanation} 先看 Step ${activeStep.index} 的图，再对照公式 ${activeStep.formula || "中的关系式"}。`
      : "先把题目拆成已知量、目标量和计算步骤，理解会比直接看答案更稳。";
  } else if (/公式|方程|kcl|kvl|det|行列式|矩阵|逆|rank|秩/.test(normalized + question)) {
    answer += activeStep?.formula
      ? `当前步骤对应的公式是：${activeStep.formula}。先确认每个符号代表什么，再代入数值。`
      : "本地模式会优先展示关键公式。";
  } else if (/答案|结果|多少/.test(question)) {
    answer += solution.visual_solution?.answer || solution.summary;
  } else {
    answer += activeStep
      ? `建议先看 Step ${activeStep.index}：${activeStep.title}。这一步想让你理解的是：${activeStep.teacher_explanation}`
      : "我可以解释步骤、公式、为什么这样做。";
  }

  return {
    answer,
    provider: "local",
    model: "local-teaching-engine",
    mode: "local"
  };
}

async function responseError(response: Response): Promise<string> {
  const body = await response.text().catch(() => "");
  const message = body.slice(0, 240);
  return `HTTP ${response.status}${message ? `：${message}` : ""}`;
}
