"use client";

import type { Profile, Provider } from "@/lib/types";

const modelsByProvider: Record<Provider, string[]> = {
  auto: ["自动选择"],
  openai: ["gpt-5", "gpt-5-mini"],
  gemini: ["gemini-pro", "gemini-flash"],
  deepseek: ["deepseek-reasoner", "deepseek-chat"]
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
    <div className="flex flex-wrap items-center justify-end gap-2">
      <select
        className="h-9 border border-neutral-300 bg-white px-3"
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
        className="h-9 border border-neutral-300 bg-white px-3"
        value={props.provider}
        onChange={(event) => {
          const provider = event.target.value as Provider;
          props.onProvider(provider);
          props.onModel("");
        }}
        aria-label="AI 供应商"
      >
        <option value="auto">自动供应商</option>
        <option value="openai">OpenAI</option>
        <option value="gemini">Gemini</option>
        <option value="deepseek">DeepSeek</option>
      </select>
      <select
        className="h-9 border border-neutral-300 bg-white px-3"
        value={props.model || ""}
        onChange={(event) => props.onModel(event.target.value)}
        aria-label="模型"
      >
        <option value="">自动选择模型</option>
        {models.map((model) => (
          <option key={model} value={model === "自动选择" ? "" : model}>
            {model}
          </option>
        ))}
      </select>
    </div>
  );
}
