export type Provider = "auto" | "openai" | "gemini" | "deepseek" | "custom";
export type Profile = "auto" | "quality" | "balanced" | "fast" | "economy";
export type Subject = "auto" | "circuit" | "linear_algebra";

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
  validation_result?: Record<string, unknown>;
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
  warnings: string[];
};
