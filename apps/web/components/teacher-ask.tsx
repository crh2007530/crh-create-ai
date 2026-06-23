"use client";

import { useState } from "react";
import { MessageCircle, Send } from "lucide-react";
import { askTeacher } from "@/lib/api";
import type { SolveResponse, TeacherAskResult } from "@/lib/types";

type ChatItem = {
  id: string;
  question: string;
  result: TeacherAskResult;
};

export function TeacherAsk(props: {
  response?: SolveResponse;
  activeStepIndex?: number;
  compact?: boolean;
}) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<ChatItem[]>([]);

  async function submit() {
    const text = question.trim();
    if (!text || loading) return;
    setQuestion("");
    setLoading(true);
    const result = await askTeacher({
      question: text,
      response: props.response,
      activeStepIndex: props.activeStepIndex
    });
    setItems((current) => [{ id: `${Date.now()}`, question: text, result }, ...current].slice(0, 4));
    setLoading(false);
  }

  return (
    <section className={props.compact ? "border border-neutral-300 bg-white p-3" : "textbook-panel p-3"}>
      <div className="mb-2 flex items-center justify-between gap-3">
        <div className="inline-flex items-center gap-2 font-extrabold">
          <MessageCircle size={17} />
          追问老师
        </div>
        <span className="text-xs text-neutral-500">可接 AI，也可本地回答</span>
      </div>

      <div className="grid gap-2">
        <textarea
          className="min-h-20 resize-y border border-neutral-300 p-3 text-sm leading-6 outline-none focus:border-neutral-900"
          placeholder="哪里看不懂？例如：为什么这里要列 KCL？"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) submit();
          }}
        />
        <button
          className="inline-flex h-10 items-center justify-center gap-2 border border-neutral-900 bg-neutral-900 px-3 text-sm font-bold text-white disabled:opacity-60"
          onClick={submit}
          disabled={loading || !question.trim()}
        >
          <Send size={15} />
          {loading ? "回答中..." : "提问"}
        </button>
      </div>

      <div className="mt-3 grid gap-2">
        {items.map((item) => (
          <div key={item.id} className="border border-neutral-300 bg-neutral-50 p-3">
            <div className="text-sm font-bold text-neutral-950">你：{item.question}</div>
            <div className="mt-2 whitespace-pre-wrap text-sm leading-6 text-neutral-800">{item.result.answer}</div>
            {item.result.error ? <div className="mt-2 border border-amber-300 bg-amber-50 p-2 text-xs text-amber-800">{item.result.error}</div> : null}
            <div className="mt-2 text-xs text-neutral-500">
              {item.result.mode === "ai" ? "AI" : "本地"} / {item.result.provider} / {item.result.model}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
