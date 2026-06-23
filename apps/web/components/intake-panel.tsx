"use client";

import { Camera, FileText, ImagePlus, Send, X } from "lucide-react";
import type { Subject } from "@/lib/types";

export function IntakePanel(props: {
  question: string;
  subject: Subject;
  fileName?: string;
  imagePreviewUrl?: string;
  loading: boolean;
  phaseLabel: string;
  onQuestion: (question: string) => void;
  onSubject: (subject: Subject) => void;
  onFile: (file: File | null) => void;
  onSolve: () => void;
}) {
  const examples = ["求图9最大功率传输", "A =\n1 2\n3 4\n求逆矩阵", "A =\n1 2\n3 4\n求矩阵的秩"];

  return (
    <section className="textbook-panel p-3 lg:p-4">
      <div className="grid gap-3 lg:grid-cols-[1fr_auto] lg:items-end">
        <textarea
          className="min-h-28 w-full resize-y border border-neutral-300 p-4 leading-7 outline-none focus:border-neutral-900"
          placeholder={"输入题目，或拍照上传题目\n例如：求矩阵A的逆矩阵\n例如：求图9最大功率传输"}
          value={props.question}
          onChange={(event) => props.onQuestion(event.target.value)}
        />
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
          <button
            className="inline-flex h-11 items-center justify-center gap-2 border border-neutral-900 bg-neutral-900 px-4 font-bold text-white disabled:opacity-60"
            onClick={props.onSolve}
            disabled={props.loading}
          >
            <Send size={16} />
            {props.loading ? props.phaseLabel || "生成中" : "开始讲题"}
          </button>
          <label className="inline-flex h-11 cursor-pointer items-center justify-center gap-2 border border-neutral-300 bg-white px-4 font-bold">
            <Camera size={16} />
            拍照/上传
            <input
              className="hidden"
              type="file"
              accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
              capture="environment"
              onChange={(event) => props.onFile(event.target.files?.[0] ?? null)}
            />
          </label>
        </div>
      </div>

      {props.imagePreviewUrl ? (
        <div className="mt-3 grid gap-2 border border-neutral-300 bg-neutral-50 p-2 sm:grid-cols-[120px_1fr_auto] sm:items-center">
          <img src={props.imagePreviewUrl} alt="题目图片预览" className="max-h-44 w-full object-contain sm:h-24" />
          <div className="min-w-0 text-sm text-neutral-700">
            <div className="flex items-center gap-1 font-bold text-neutral-950">
              <ImagePlus size={15} />
              图片已选择
            </div>
            <div className="mt-1 truncate">{props.fileName}</div>
            <div className="mt-1 text-neutral-500">点击“开始讲题”后会先识别题目文本。</div>
          </div>
          <button className="inline-flex h-9 items-center justify-center gap-1 border border-neutral-300 bg-white px-3" onClick={() => props.onFile(null)}>
            <X size={15} />
            移除
          </button>
        </div>
      ) : props.fileName ? (
        <div className="mt-3 inline-flex items-center gap-1 text-sm text-neutral-600">
          <FileText size={14} />
          {props.fileName}
        </div>
      ) : null}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <select
          className="h-9 border border-neutral-300 bg-white px-2"
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
            className="min-h-9 whitespace-pre-line border border-neutral-300 bg-neutral-50 px-3 text-left text-sm"
            onClick={() => props.onQuestion(example)}
          >
            {example}
          </button>
        ))}
      </div>
    </section>
  );
}
