import type { SolveResponse, SolutionStep } from "@/lib/types";
import { StepList } from "./step-list";
import { VisualizationPanel } from "./visualization-panel";

export function ResultLayout(props: {
  response?: SolveResponse;
  activeIndex: number;
  onStep: (index: number) => void;
}) {
  const solution = props.response?.solution;
  const activeStep: SolutionStep | undefined = solution?.steps[props.activeIndex];

  if (!solution) {
    return (
      <section className="textbook-panel grid min-h-48 place-items-center p-6 text-center text-neutral-500">
        结果会显示为答案卡、验证卡和可展开步骤图。
      </section>
    );
  }

  return (
    <>
      <section className="grid gap-3 lg:hidden">
        <AnswerCard response={props.response} />
        <ValidationCard response={props.response} />
        <ModelCard response={props.response} />
        <MobileStepList steps={solution.steps} />
      </section>

      <section className="hidden gap-3 lg:grid lg:grid-cols-[25fr_35fr_40fr]">
        <aside className="textbook-panel p-3">
          <QuestionCard response={props.response} />
          <div className="mt-3">
            <ModelCard response={props.response} compact />
          </div>
        </aside>

        <section className="textbook-panel p-3">
          <div className="mb-3 flex items-center justify-between border-b border-neutral-300 pb-2">
            <span className="font-extrabold">板书步骤</span>
            <span className="text-sm text-neutral-600">
              {activeStep ? `Step ${activeStep.index} / ${solution.steps.length}` : "未生成"}
            </span>
          </div>
          <StepList steps={solution.steps} activeIndex={props.activeIndex} onStep={props.onStep} />
          <div className="mt-3 border border-neutral-300 bg-white p-3">
            <div className="mb-2 text-xs font-bold text-neutral-500">公式</div>
            <div className="whitespace-pre-wrap font-mono leading-7">{activeStep?.formula ?? "-"}</div>
          </div>
          <div className="mt-3 border-l-4 border-neutral-950 bg-neutral-50 p-3 leading-7">
            <strong className="block">为什么这样做？</strong>
            {activeStep?.teacher_explanation ?? "-"}
          </div>
        </section>

        <section>
          <VisualizationPanel step={activeStep} confirmationRequired={solution.confirmation_required} />
        </section>
      </section>
    </>
  );
}

function QuestionCard(props: { response?: SolveResponse }) {
  const solution = props.response?.solution;
  return (
    <div>
      <div className="mb-3 border-b border-neutral-300 pb-2 font-extrabold">原题</div>
      <div className="min-h-28 whitespace-pre-wrap border border-dashed border-neutral-400 bg-neutral-50 p-4 text-sm leading-7 text-neutral-700">
        {solution?.problem.original_text ?? "-"}
      </div>
      <div className="mt-3 grid gap-2 border-t border-neutral-300 pt-3 text-sm text-neutral-600">
        <MetaRow label="科目" value={solution?.problem.subject ?? "-"} />
        <MetaRow label="主题" value={solution?.problem.topic ?? "-"} />
        {props.response?.warnings.map((warning) => (
          <div key={warning} className="border border-amber-300 bg-amber-50 p-2 text-amber-800">
            {warning}
          </div>
        ))}
      </div>
    </div>
  );
}

function AnswerCard(props: { response?: SolveResponse }) {
  const solution = props.response?.solution;
  return (
    <section className="textbook-panel p-3">
      <div className="mb-2 font-extrabold">答案</div>
      <div className="whitespace-pre-wrap bg-neutral-50 p-3 font-mono leading-7">
        {solution?.visual_solution?.answer || solution?.summary || "已生成步骤，请展开查看。"}
      </div>
    </section>
  );
}

function ValidationCard(props: { response?: SolveResponse }) {
  const validation = props.response?.solution.validation_result;
  const summary = props.response?.solution.visual_solution?.validationSummary;
  const passed = validation?.passed;
  return (
    <section className="textbook-panel p-3">
      <div className="mb-2 font-extrabold">验证</div>
      <div className={["border p-3", passed === false ? "border-amber-300 bg-amber-50" : "border-green-300 bg-green-50"].join(" ")}>
        <div className="font-bold">{summary || (passed ? "Verified" : "Teaching Preview")}</div>
        <div className="mt-1 text-sm text-neutral-700">
          {validation ? `验证得分：${Math.round(validation.score * 100)}%` : "当前步骤图可用于学习预览。"}
        </div>
      </div>
    </section>
  );
}

function ModelCard(props: { response?: SolveResponse; compact?: boolean }) {
  const route = props.response?.model_route ?? {};
  const provider = props.response?.provider ?? route.reason_provider ?? "-";
  const model = props.response?.model ?? route.reason_model ?? "-";
  const status = props.response?.model_status ?? "template";
  return (
    <section className={props.compact ? "" : "textbook-panel p-3"}>
      <div className="mb-2 font-extrabold">模型调用</div>
      <div className="grid gap-2 text-sm text-neutral-700">
        <MetaRow label="Provider" value={provider} />
        <MetaRow label="Model" value={model} />
        <MetaRow label="状态" value={statusLabel(status)} />
        {route.vision_provider && route.vision_provider !== "none" ? <MetaRow label="Vision" value={`${route.vision_provider} / ${route.vision_model}`} /> : null}
      </div>
    </section>
  );
}

function MobileStepList(props: { steps: SolutionStep[] }) {
  return (
    <section className="grid gap-2">
      <div className="font-extrabold">步骤</div>
      {props.steps.map((step, index) => (
        <details key={step.id} className="textbook-panel group" open={index === 0}>
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-3">
            <span>
              <span className="font-serif font-black">Step {step.index}</span>
              <span className="ml-3 font-extrabold">{step.title}</span>
            </span>
            <span className="text-sm text-neutral-500 group-open:hidden">展开</span>
            <span className="hidden text-sm text-neutral-500 group-open:inline">收起</span>
          </summary>
          <div className="border-t border-neutral-300 p-3">
            <div className="safe-svg border border-neutral-300 bg-white" dangerouslySetInnerHTML={{ __html: step.visualization.svg }} />
            <div className="mt-3 border-l-4 border-neutral-950 bg-neutral-50 p-3 leading-7">
              <strong className="block">为什么这样做？</strong>
              {step.teacher_explanation}
            </div>
            <div className="mt-3 whitespace-pre-wrap border border-neutral-300 bg-white p-3 font-mono text-sm leading-6">
              {step.formula}
            </div>
          </div>
        </details>
      ))}
    </section>
  );
}

function MetaRow(props: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <span>{props.label}</span>
      <strong className="text-right text-neutral-950">{props.value}</strong>
    </div>
  );
}

function statusLabel(status: string) {
  if (status === "real_ai") return "真实 AI 调用";
  if (status === "provider_fallback") return "AI 不可用，已回退";
  if (status === "engine_template") return "引擎 + 教学模板";
  return status;
}
