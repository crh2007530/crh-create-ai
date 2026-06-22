"use client";

import { ImagePlus, Send, FileText } from "lucide-react";
import type { Subject } from "@/lib/types";

export function IntakePanel(props: {
  question: string;
  subject: Subject;
  fileName?: string;
  loading: boolean;
  onQuestion: (question: string) => void;
  onSubject: (subject: Subject) => void;
  onFile: (file: File | null) => void;
  onSolve: () => void;
}) {
  const examples = ["求图9最大功率传输", "求矩阵A的逆矩阵", "求三相负载线电流"];

  return (
    <section className="textbook-panel p-4">
      <div className="grid gap-3 lg:grid-cols-[1fr_auto] lg:items-end">
        <textarea
          className="min-h-28 w-full resize-y border border-neutral-300 p-4 leading-7 outline-none focus:border-neutral-900"
          placeholder={"求图9最大功率传输\n求矩阵A的逆矩阵\n求三相负载线电流"}
          value={props.question}
          onChange={(event) => props.onQuestion(event.target.value)}
        />
        <div className="grid gap-2">
          <button
            className="inline-flex h-10 items-center justify-center gap-2 border border-neutral-900 bg-neutral-900 px-4 font-bold text-white"
            onClick={props.onSolve}
            disabled={props.loading}
          >
            <Send size={16} />
            {props.loading ? "生成中" : "开始讲题"}
          </button>
          <label className="inline-flex h-10 cursor-pointer items-center justify-center gap-2 border border-neutral-300 bg-white px-4 font-bold">
            <ImagePlus size={16} />
            上传图片/PDF
            <input
              className="hidden"
              type="file"
              accept="image/*,.pdf"
              onChange={(event) => props.onFile(event.target.files?.[0] ?? null)}
            />
          </label>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <select
          className="h-8 border border-neutral-300 bg-white px-2"
          value={props.subject}
          onChange={(event) => props.onSubject(event.target.value as Subject)}
          aria-label="科目"
        >
          <option value="auto">自动识别</option>
          <option value="circuit">电路分析</option>
          <option value="linear_algebra">线性代数</option>
        </select>
        {examples.map((example) => (
          <button
            key={example}
            className="min-h-8 border border-neutral-300 bg-neutral-50 px-3"
            onClick={() => props.onQuestion(example)}
          >
            {example}
          </button>
        ))}
        {props.fileName ? (
          <span className="inline-flex items-center gap-1 text-sm text-neutral-600">
            <FileText size={14} />
            {props.fileName}
          </span>
        ) : null}
      </div>
    </section>
  );
}
