"use client";

import { BrainCircuit, ChevronDown } from "lucide-react";
import { ApiSettings } from "./api-settings";
import type { ApiConfig, Profile, Provider } from "@/lib/types";

export function modelLabel(provider: Provider, model: string) {
  const resolvedProvider = provider === "auto" ? "openai" : provider;
  const resolvedModel =
    model ||
    (resolvedProvider === "openai"
      ? "gpt-5.5"
      : resolvedProvider === "gemini"
        ? "gemini-2.5-pro"
        : resolvedProvider === "deepseek"
          ? "deepseek-v3"
          : "custom-model");
  const providerName =
    resolvedProvider === "openai"
      ? "OpenAI"
      : resolvedProvider === "gemini"
        ? "Gemini"
        : resolvedProvider === "deepseek"
          ? "DeepSeek"
          : "Custom";
  return `${providerName} · ${resolvedModel}`;
}

export function ModelSelector(props: {
  provider: Provider;
  profile: Profile;
  model: string;
  onProvider: (provider: Provider) => void;
  onProfile: (profile: Profile) => void;
  onModel: (model: string) => void;
}) {
  function handleSaved(config: ApiConfig | null) {
    props.onProvider(config?.provider ?? "auto");
    props.onModel(config?.model ?? "");
    props.onProfile("auto");
  }

  return (
    <details className="border-t border-neutral-300 pt-3">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3">
        <span className="inline-flex items-center gap-2 text-sm font-bold">
          <BrainCircuit size={16} />
          高级设置
        </span>
        <span className="inline-flex items-center gap-1 text-xs text-neutral-600">
          当前模型：{modelLabel(props.provider, props.model)}
          <ChevronDown size={14} />
        </span>
      </summary>
      <ApiSettings onSaved={handleSaved} />
    </details>
  );
}
