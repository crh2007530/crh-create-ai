"use client";

import { BrainCircuit, ChevronDown } from "lucide-react";
import type { Profile, Provider } from "@/lib/types";

const modelsByProvider: Record<Provider, string[]> = {
  auto: ["gpt-5.5"],
  openai: ["gpt-5.5", "gpt-5.5-mini"],
  gemini: ["gemini-2.5-pro", "gemini-2.5-flash"],
  deepseek: ["deepseek-v3", "deepseek-reasoner", "deepseek-chat"],
  custom: ["custom-model", "OpenAI Compatible"]
};

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
  const models = modelsByProvider[props.provider] ?? modelsByProvider.auto;

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

      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        <select
          className="h-10 border border-neutral-300 bg-white px-3 text-sm"
          value={props.provider}
          onChange={(event) => {
            const provider = event.target.value as Provider;
            props.onProvider(provider);
            props.onModel("");
          }}
          aria-label="AI Provider"
        >
          <option value="auto">自动选择</option>
          <option value="openai">OpenAI</option>
          <option value="gemini">Gemini</option>
          <option value="deepseek">DeepSeek</option>
          <option value="custom">Custom API</option>
        </select>

        <select
          className="h-10 border border-neutral-300 bg-white px-3 text-sm"
          value={props.model || ""}
          onChange={(event) => props.onModel(event.target.value)}
          aria-label="Model"
        >
          <option value="">自动模型</option>
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>

        <select
          className="h-10 border border-neutral-300 bg-white px-3 text-sm"
          value={props.profile}
          onChange={(event) => props.onProfile(event.target.value as Profile)}
          aria-label="Profile"
        >
          <option value="auto">自动推荐</option>
          <option value="quality">高质量</option>
          <option value="balanced">平衡</option>
          <option value="fast">快速</option>
          <option value="economy">省钱</option>
        </select>
      </div>

      <div className="mt-2 text-xs leading-5 text-neutral-500">
        API Key 在后端环境变量中配置；公网静态预览没有 Key 时会显示 Template / Engine 模式。
      </div>
    </details>
  );
}
