import type { Profile, Provider, SolveResponse, Subject } from "./types";
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
  const localOnly = process.env.NEXT_PUBLIC_LOCAL_SOLVER === "true";
  if (localOnly) {
    return solveLocally(input);
  }

  const form = new FormData();
  form.set("question", input.question);
  form.set("subject", input.subject);
  form.set("provider", input.provider);
  form.set("profile", input.profile);
  if (input.model) form.set("model", input.model);
  if (input.file) form.set("file", input.file);

  const response = await fetch(`${API_URL}/solve`, {
    method: "POST",
    body: form
  }).catch(() => null);

  if (!response || !response.ok) {
    return solveLocally(input);
  }

  try {
    return await response.json();
  } catch {
    return solveLocally(input);
  }
}
