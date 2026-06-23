"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, KeyRound, Trash2 } from "lucide-react";
import { clearApiConfig, createDefaultApiConfig, loadApiConfig, saveApiConfig } from "@/lib/api-config";
import { testProvider } from "@/lib/api";
import type { ApiConfig, Provider } from "@/lib/types";

export function ApiSettings(props: { onSaved?: (config: ApiConfig | null) => void }) {
  const [config, setConfig] = useState<ApiConfig>(() => createDefaultApiConfig("custom"));
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const saved = loadApiConfig();
    if (saved) setConfig(saved);
  }, []);

  function updateProvider(provider: Provider) {
    setConfig(createDefaultApiConfig(provider === "auto" ? "custom" : provider));
    setMessage("");
  }

  function save() {
    saveApiConfig(config);
    props.onSaved?.(config);
    setMessage("已保存到当前浏览器。普通用户不需要填写这里。");
  }

  function remove() {
    clearApiConfig();
    const next = createDefaultApiConfig("custom");
    setConfig(next);
    props.onSaved?.(null);
    setMessage("已清除自定义 API，恢复平台默认识题。");
  }

  async function test() {
    setTesting(true);
    setMessage("");
    const result = await testProvider(config);
    setTesting(false);
    setMessage(result.success ? `连接成功：${result.provider} / ${result.model}` : `连接失败：${result.error}`);
  }

  return (
    <div className="mt-3 border border-neutral-300 bg-neutral-50 p-3">
      <div className="mb-3 flex items-center gap-2 font-extrabold">
        <KeyRound size={16} />
        自定义 AI 配置
      </div>
      <div className="mb-3 border border-neutral-300 bg-white p-2 text-sm leading-6 text-neutral-600">
        普通用户无需填写。拍照识题默认走平台后端；这里仅给开发者或高级用户自带 API 使用。
      </div>
      <div className="grid gap-2">
        <label className="grid gap-1 text-sm">
          <span className="font-bold">Provider</span>
          <select className="h-10 border border-neutral-300 bg-white px-3" value={config.provider} onChange={(event) => updateProvider(event.target.value as Provider)}>
            <option value="custom">平台兼容接口</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
            <option value="deepseek">DeepSeek</option>
          </select>
        </label>
        <label className="grid gap-1 text-sm">
          <span className="font-bold">API Key</span>
          <input className="h-10 border border-neutral-300 bg-white px-3" type="password" value={config.apiKey} onChange={(event) => setConfig({ ...config, apiKey: event.target.value })} placeholder="sk-..." />
        </label>
        <label className="grid gap-1 text-sm">
          <span className="font-bold">Base URL</span>
          <input className="h-10 border border-neutral-300 bg-white px-3" value={config.baseUrl} onChange={(event) => setConfig({ ...config, baseUrl: event.target.value })} placeholder="https://ai-pixel.online" />
        </label>
        <label className="grid gap-1 text-sm">
          <span className="font-bold">Model</span>
          <input className="h-10 border border-neutral-300 bg-white px-3" value={config.model} onChange={(event) => setConfig({ ...config, model: event.target.value })} placeholder="gpt-4o-mini" />
        </label>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <button className="border border-neutral-900 bg-neutral-900 px-3 py-2 text-sm font-bold text-white disabled:opacity-60" onClick={test} disabled={testing || !config.apiKey}>
          {testing ? "测试中" : "测试连接"}
        </button>
        <button className="inline-flex items-center justify-center gap-1 border border-neutral-300 bg-white px-3 py-2 text-sm font-bold" onClick={save}>
          <CheckCircle2 size={15} />
          保存
        </button>
        <button className="inline-flex items-center justify-center gap-1 border border-neutral-300 bg-white px-3 py-2 text-sm font-bold" onClick={remove}>
          <Trash2 size={15} />
          清除
        </button>
      </div>
      {message ? <div className="mt-2 text-sm text-neutral-700">{message}</div> : null}
      <div className="mt-2 text-xs leading-5 text-neutral-500">自定义 API Key 只保存在当前浏览器 localStorage 中。</div>
    </div>
  );
}
