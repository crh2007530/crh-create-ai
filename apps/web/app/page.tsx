"use client";

import { useState } from "react";
import { IntakePanel } from "@/components/intake-panel";
import { ModelSelector } from "@/components/model-selector";
import { ResultLayout } from "@/components/result-layout";
import { solveProblem } from "@/lib/api";
import type { Profile, Provider, SolveResponse, Subject } from "@/lib/types";

export default function HomePage() {
  const [question, setQuestion] = useState("A =\n1 2\n3 4\n求行列式");
  const [subject, setSubject] = useState<Subject>("auto");
  const [provider, setProvider] = useState<Provider>("auto");
  const [profile, setProfile] = useState<Profile>("auto");
  const [model, setModel] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<SolveResponse>();
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSolve() {
    setLoading(true);
    setError("");
    try {
      const result = await solveProblem({ question, subject, provider, profile, model, file });
      setResponse(result);
      setActiveIndex(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen">
      <header className="sticky top-0 z-10 flex flex-col gap-3 border-b border-neutral-300 bg-white p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center border-2 border-neutral-950 font-black">c</div>
          <div>
            <h1 className="text-lg font-black leading-5">crh create AI</h1>
            <p className="text-xs text-neutral-600">工科版 Photomath，可视化解题平台</p>
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
          loading={loading}
          onQuestion={setQuestion}
          onSubject={setSubject}
          onFile={setFile}
          onSolve={handleSolve}
        />
        {error ? <div className="border border-red-300 bg-red-50 p-3 text-red-700">{error}</div> : null}
        <ResultLayout response={response} activeIndex={activeIndex} onStep={setActiveIndex} />
      </div>
    </main>
  );
}
