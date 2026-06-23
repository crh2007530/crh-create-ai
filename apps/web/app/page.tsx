"use client";

import { useEffect, useMemo, useState } from "react";
import { IntakePanel } from "@/components/intake-panel";
import { modelLabel, ModelSelector } from "@/components/model-selector";
import { ResultLayout } from "@/components/result-layout";
import { loadApiConfig } from "@/lib/api-config";
import { solveProblem } from "@/lib/api";
import type { Profile, Provider, SolvePhase, SolveResponse, Subject } from "@/lib/types";

export default function HomePage() {
  const [question, setQuestion] = useState("A =\n1 2\n3 4\n求行列式");
  const [subject, setSubject] = useState<Subject>("auto");
  const [provider, setProvider] = useState<Provider>("auto");
  const [profile, setProfile] = useState<Profile>("auto");
  const [model, setModel] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<SolveResponse>();
  const [activeIndex, setActiveIndex] = useState(0);
  const [phase, setPhase] = useState<SolvePhase>("idle");
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = loadApiConfig();
    if (saved) {
      setProvider(saved.provider);
      setModel(saved.model);
    }
  }, []);

  const currentModel = modelLabel(provider, model);
  const loading = !["idle", "done", "error"].includes(phase);
  const phaseLabel = getPhaseLabel(phase, currentModel);
  const fileKind = file?.type.startsWith("image/") ? "image" : file?.type === "application/pdf" ? "pdf" : "file";
  const imagePreviewUrl = useMemo(() => {
    if (!file || !file.type.startsWith("image/")) return "";
    return URL.createObjectURL(file);
  }, [file]);

  useEffect(() => {
    return () => {
      if (imagePreviewUrl) URL.revokeObjectURL(imagePreviewUrl);
    };
  }, [imagePreviewUrl]);

  async function handleSolve() {
    setError("");
    setResponse(undefined);
    setPhase(file ? "recognizing" : "parsing");
    try {
      if (file) await delay(200);
      setPhase(file ? "recognizing" : "parsing");
      const result = await solveProblem({ question, subject, provider, profile, model, file });
      setPhase("calculating");
      await delay(120);
      setPhase("validating");
      await delay(120);
      if (result.extracted_text) setQuestion(result.extracted_text);
      setResponse(result);
      setActiveIndex(0);
      setPhase("done");
    } catch (err) {
      setPhase("error");
      setResponse(undefined);
      setError(err instanceof Error ? err.message : "生成失败，请检查 API 配置或稍后重试。");
    }
  }

  return (
    <main className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-neutral-300 bg-white px-3 py-3">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center border-2 border-neutral-950 font-black">c</div>
            <div>
              <h1 className="text-lg font-black leading-5">crh create AI</h1>
              <p className="text-xs text-neutral-600">用户自己的 AI + 教学可视化引擎</p>
            </div>
          </div>
          <div className="hidden text-right text-xs text-neutral-600 sm:block">
            当前模型
            <div className="font-bold text-neutral-950">{currentModel}</div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-4 p-3 lg:p-5">
        <IntakePanel
          question={question}
          subject={subject}
          fileName={file?.name}
          fileKind={file ? fileKind : undefined}
          imagePreviewUrl={imagePreviewUrl}
          loading={loading}
          phaseLabel={phaseLabel}
          onQuestion={setQuestion}
          onSubject={setSubject}
          onFile={setFile}
          onSolve={handleSolve}
        >
          <ModelSelector
            provider={provider}
            profile={profile}
            model={model}
            onProvider={setProvider}
            onProfile={setProfile}
            onModel={setModel}
          />
        </IntakePanel>

        {error ? (
          <section className="border border-red-300 bg-red-50 p-4 text-red-800">
            <div className="font-extrabold">无法生成可视化</div>
            <p className="mt-1 text-sm leading-6">{error}</p>
            <div className="mt-3 grid gap-2 text-sm leading-6">
              <p>上传图片/PDF 时，必须先在高级设置保存支持视觉识别的 API Key。</p>
              <p>如果只是想试线性代数可视化，可以直接把题目文字输入到上方文本框。</p>
            </div>
            <button className="mt-3 border border-red-300 bg-white px-3 py-2 font-bold" onClick={handleSolve}>
              重试
            </button>
          </section>
        ) : null}

        <ResultLayout response={response} activeIndex={activeIndex} onStep={setActiveIndex} />
      </div>
    </main>
  );
}

function getPhaseLabel(phase: SolvePhase, model: string) {
  if (phase === "recognizing") return `正在调用 ${model} 识别题目...`;
  if (phase === "parsing") return "正在解析题目...";
  if (phase === "calculating") return "正在生成教学步骤图...";
  if (phase === "validating") return "正在验证结果...";
  if (phase === "done") return "已生成";
  if (phase === "error") return "生成失败";
  return "";
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
