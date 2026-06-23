"use client";

import type { ReactNode } from "react";
import { Camera, FileText, ImageUp, Send, X } from "lucide-react";
import type { Subject } from "@/lib/types";

export function IntakePanel(props: {
  question: string;
  subject: Subject;
  fileName?: string;
  fileKind?: "image" | "pdf" | "file";
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
          placeholder={"输入题目，或拍照/上传题目图片/PDF\n例如：A = 1 2 / 3 4，求行列式"}
          value={props.question}
          onChange={(event) => props.onQuestion(event.target.value)}
        />

        <div className="grid grid-cols-3 gap-2 text-sm">
          <SubjectButton active={props.subject === "auto"} onClick={() => props.onSubject("auto")}>
            自动识别
          </SubjectButton>
          <SubjectButton active={props.subject === "linear_algebra"} onClick={() => props.onSubject("linear_algebra")}>
            线性代数
          </SubjectButton>
          <SubjectButton active={props.subject === "circuit"} onClick={() => props.onSubject("circuit")}>
            电路分析
          </SubjectButton>
        </div>

        {props.fileName ? (
          <div className="grid gap-2 border border-neutral-300 bg-neutral-50 p-2 sm:grid-cols-[120px_1fr_auto] sm:items-center">
            {props.imagePreviewUrl ? (
              <img src={props.imagePreviewUrl} alt="题目图片预览" className="max-h-44 w-full object-contain sm:h-24" />
            ) : (
              <div className="grid h-24 place-items-center border border-neutral-300 bg-white">
                <FileText size={34} />
              </div>
            )}
            <div className="min-w-0 text-sm text-neutral-700">
              <div className="font-bold text-neutral-950">{props.fileKind === "pdf" ? "PDF 已选择" : "文件已选择"}</div>
              <div className="mt-1 truncate">{props.fileName}</div>
              <div className="mt-1 text-neutral-500">如果识别错科目，可先切换“线性代数/电路分析”再开始讲题。</div>
            </div>
            <button className="inline-flex h-9 items-center justify-center gap-1 border border-neutral-300 bg-white px-3" onClick={() => props.onFile(null)}>
              <X size={15} />
              移除
            </button>
          </div>
        ) : null}

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-[1fr_1fr_1.3fr]">
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
          <label className="inline-flex h-12 cursor-pointer items-center justify-center gap-2 border border-neutral-300 bg-white px-4 font-bold">
            <ImageUp size={18} />
            上传
            <input
              className="hidden"
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf,.jpg,.jpeg,.png,.webp,.pdf"
              onChange={(event) => props.onFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button
            className="col-span-2 inline-flex h-12 items-center justify-center gap-2 border border-neutral-900 bg-neutral-900 px-4 font-bold text-white disabled:opacity-60 sm:col-span-1"
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

function SubjectButton(props: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      className={[
        "h-10 border px-2 font-bold",
        props.active ? "border-neutral-950 bg-neutral-950 text-white" : "border-neutral-300 bg-white text-neutral-800"
      ].join(" ")}
      onClick={props.onClick}
      type="button"
    >
      {props.children}
    </button>
  );
}
