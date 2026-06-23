"use client";

import { useEffect, useMemo, useState } from "react";
import { IntakePanel } from "@/components/intake-panel";
import { ModelSelector } from "@/components/model-selector";
import { ResultLayout } from "@/components/result-layout";
import { solveProblem } from "@/lib/api";
import type { Profile, Provider, SolvePhase, SolveResponse, Subject } from "@/lib/types";

const phaseLabels: Record<SolvePhase, string> = {
  idle: "",
  recognizing: "正在识别题目...",
  parsing: "正在解析题目...",
  calculating: "正在计算...",
  validating: "正在验证结果...",
  done: "已生成",
  error: "生成失败"
};

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

  const loading = !["idle", "done", "error"].includes(phase);
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
    setPhase(file ? "recognizing" : "parsing");
    try {
      if (file) await delay(450);
      setPhase("parsing");
      await delay(250);
      setPhase("calculating");
      const result = await solveProblem({ question, subject, provider, profile, model, file });
      setPhase("validating");
      await delay(250);
      setResponse(result);
      setActiveIndex(0);
      setPhase("done");
    } catch (err) {
      setPhase("error");
      setError(err instanceof Error ? err.message : "生成失败，请检查模型配置或稍后重试。");
    }
  }

  return (
    <main className="min-h-screen">
      <header className="sticky top-0 z-10 flex flex-col gap-3 border-b border-neutral-300 bg-white p-3 lg:flex-row lg:items-center lg:justify-between lg:p-4">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 shrink-0 place-items-center border-2 border-neutral-950 font-black">c</div>
          <div>
            <h1 className="text-lg font-black leading-5">crh create AI</h1>
            <p className="text-xs text-neutral-600">拍照、识题、看步骤图</p>
          </div>
        </div>
        <ModelSelector
          provider={provider}
          profile={profile}
          model={model}
          onProvider={setProvider}
          onProfile={setProfile}
          onModel={setModel}
        />
      </header>

      <div className="grid gap-4 p-3 lg:p-5">
        <IntakePanel
          question={question}
          subject={subject}
          fileName={file?.name}
          imagePreviewUrl={imagePreviewUrl}
          loading={loading}
          phaseLabel={phaseLabels[phase]}
          onQuestion={setQuestion}
          onSubject={setSubject}
          onFile={setFile}
          onSolve={handleSolve}
        />

        {error ? (
          <section className="border border-red-300 bg-red-50 p-4 text-red-800">
            <div className="font-extrabold">出错了</div>
            <p className="mt-1 text-sm leading-6">{error}</p>
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

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
