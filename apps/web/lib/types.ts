export type Provider = "auto" | "openai" | "gemini" | "deepseek" | "custom";
export type Profile = "auto" | "quality" | "balanced" | "fast" | "economy";
export type Subject = "auto" | "circuit" | "linear_algebra";

export type ApiProvider = Exclude<Provider, "auto">;

export type ApiConfig = {
  provider: ApiProvider;
  apiKey: string;
  baseUrl: string;
  model: string;
};

export type ProviderTestResult = {
  success: boolean;
  provider: string;
  model: string;
  error?: string;
};

export type TeacherAskResult = {
  answer: string;
  provider: string;
  model: string;
  mode: "ai" | "local";
  error?: string;
};

export type Visualization = {
  id: string;
  kind: "circuit_svg" | "matrix_svg" | "overlay_svg";
  mode: "textbook" | "analysis" | "overlay";
  svg: string;
  highlights: string[];
};

export type SolutionStep = {
  id: string;
  index: number;
  title: string;
  teacher_explanation: string;
  formula: string;
  visualization: Visualization;
};

export type SolvePhase = "idle" | "recognizing" | "parsing" | "calculating" | "validating" | "done" | "error";

export type Solution = {
  id: string;
  summary: string;
  confirmation_required: boolean;
  visual_solution?: {
    answer: string;
    confidence: number;
    topic?: string;
    difficulty?: number;
    validationSummary?: string;
  };
  problem_document?: Record<string, unknown>;
  math_result?: Record<string, unknown>;
  validation_result?: {
    passed: boolean;
    score: number;
    checks?: Array<{ name: string; passed: boolean; message?: string }>;
    metadata?: Record<string, unknown>;
  };
  problem: {
    id: string;
    input_mode: "text" | "image" | "paste" | "pdf";
    subject: "circuit" | "linear_algebra";
    topic: string;
    original_text: string;
  };
  steps: SolutionStep[];
};

export type SolveResponse = {
  solution: Solution;
  model_route: Record<string, string>;
  provider?: string | null;
  model?: string | null;
  model_status?: string;
  extracted_text?: string;
  warnings: string[];
};
