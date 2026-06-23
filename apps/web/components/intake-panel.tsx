"use client";

import type { ReactNode } from "react";
import { Camera, Send, X } from "lucide-react";
import type { Subject } from "@/lib/types";

export function IntakePanel(props: {
  question: string;
  subject: Subject;
  fileName?: string;
  imagePreviewUrl?: string;
  loading: boolean;
  phaseLabel: string;
  children?: ReactNode;
  onQuestion: (question: string) => void;
  onSubject: (subject: Subject) => void;
  onFile: (file: File | null) => void;
  onSolve: () => void;
}) {
  return (
    <section className="textbook-panel p-3 lg:p-4">
      <div className="grid gap-3">
        <textarea
          className="min-h-36 w-full resize-y border border-neutral-300 p-4 text-base leading-7 outline-none focus:border-neutral-900"
          placeholder={"输入题目，或拍照上传题目\n例如：A = 1 2 / 3 4，求行列式"}
          value={props.question}
          onChange={(event) => props.onQuestion(event.target.value)}
        />

        {props.imagePreviewUrl ? (
          <div className="grid gap-2 border border-neutral-300 bg-neutral-50 p-2 sm:grid-cols-[120px_1fr_auto] sm:items-center">
            <img src={props.imagePreviewUrl} alt="题目图片预览" className="max-h-44 w-full object-contain sm:h-24" />
            <div className="min-w-0 text-sm text-neutral-700">
              <div className="font-bold text-neutral-950">图片已选择</div>
              <div className="mt-1 truncate">{props.fileName}</div>
              <div className="mt-1 text-neutral-500">开始讲题后会先识别题目文本。</div>
            </div>
            <button className="inline-flex h-9 items-center justify-center gap-1 border border-neutral-300 bg-white px-3" onClick={() => props.onFile(null)}>
              <X size={15} />
              移除
            </button>
          </div>
        ) : null}

        <div className="grid grid-cols-2 gap-2">
          <label className="inline-flex h-12 cursor-pointer items-center justify-center gap-2 border border-neutral-300 bg-white px-4 font-bold">
            <Camera size={18} />
            拍照
            <input
              className="hidden"
              type="file"
              accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
              capture="environment"
              onChange={(event) => props.onFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button
            className="inline-flex h-12 items-center justify-center gap-2 border border-neutral-900 bg-neutral-900 px-4 font-bold text-white disabled:opacity-60"
            onClick={props.onSolve}
            disabled={props.loading}
          >
            <Send size={18} />
            {props.loading ? props.phaseLabel || "生成中" : "开始讲题"}
          </button>
        </div>

        {props.children}
      </div>
    </section>
  );
}
