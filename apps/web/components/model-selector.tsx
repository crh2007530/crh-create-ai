"use client";

import { BrainCircuit } from "lucide-react";
import type { Profile, Provider } from "@/lib/types";

const modelsByProvider: Record<Provider, string[]> = {
  auto: ["自动选择"],
  openai: ["gpt-5", "gpt-5-mini"],
  gemini: ["gemini-pro", "gemini-flash"],
  deepseek: ["deepseek-reasoner", "deepseek-chat"],
  custom: ["OpenAI Compatible"]
};

export function ModelSelector(props: {
  provider: Provider;
  profile: Profile;
  model: string;
  onProvider: (provider: Provider) => void;
  onProfile: (profile: Profile) => void;
  onModel: (model: string) => void;
}) {
  const models = modelsByProvider[props.provider] ?? modelsByProvider.auto;

  return (
    <div className="grid gap-2 sm:flex sm:flex-wrap sm:items-center sm:justify-end">
      <label className="inline-flex h-10 items-center gap-2 border border-neutral-300 bg-white px-3">
        <BrainCircuit size={16} />
        <span className="text-sm font-bold">Model</span>
        <select
          className="min-w-0 bg-transparent text-sm outline-none"
          value={props.provider}
          onChange={(event) => {
            const provider = event.target.value as Provider;
            props.onProvider(provider);
            props.onModel("");
          }}
          aria-label="AI 供应商"
        >
          <option value="auto">自动</option>
          <option value="openai">OpenAI</option>
          <option value="gemini">Gemini</option>
          <option value="deepseek">DeepSeek</option>
          <option value="custom">Custom</option>
        </select>
      </label>

      <div className="grid grid-cols-2 gap-2 sm:flex">
        <select
          className="h-10 border border-neutral-300 bg-white px-3 text-sm"
          value={props.profile}
          onChange={(event) => props.onProfile(event.target.value as Profile)}
          aria-label="模型模式"
        >
          <option value="auto">自动推荐</option>
          <option value="quality">高质量</option>
          <option value="balanced">平衡</option>
          <option value="fast">快速</option>
          <option value="economy">省钱</option>
        </select>
        <select
          className="h-10 border border-neutral-300 bg-white px-3 text-sm"
          value={props.model || ""}
          onChange={(event) => props.onModel(event.target.value)}
          aria-label="模型"
        >
          <option value="">自动模型</option>
          {models.map((model) => (
            <option key={model} value={model === "自动选择" ? "" : model}>
              {model}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
