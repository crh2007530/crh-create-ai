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

  return (
    <section className="grid gap-3 lg:grid-cols-[25fr_35fr_40fr]">
      <aside className="textbook-panel p-3">
        <div className="mb-3 border-b border-neutral-300 pb-2 font-extrabold">原题</div>
        <div className="min-h-44 border border-dashed border-neutral-400 bg-neutral-50 p-4 text-sm leading-7 text-neutral-600">
          {solution?.problem.original_text ?? "输入文字、上传图片、粘贴截图或上传 PDF 后，系统先识别题目，再重画电路图/矩阵结构。"}
        </div>
        <div className="mt-3 grid gap-2 border-t border-neutral-300 pt-3 text-sm text-neutral-600">
          <div className="flex justify-between gap-3">
            <span>科目</span>
            <strong className="text-right text-neutral-950">{solution?.problem.subject ?? "-"}</strong>
          </div>
          <div className="flex justify-between gap-3">
            <span>主题</span>
            <strong className="text-right text-neutral-950">{solution?.problem.topic ?? "-"}</strong>
          </div>
          <div className="flex justify-between gap-3">
            <span>视觉模型</span>
            <strong className="text-right text-neutral-950">{props.response?.model_route.vision_model ?? "-"}</strong>
          </div>
          <div className="flex justify-between gap-3">
            <span>推理模型</span>
            <strong className="text-right text-neutral-950">{props.response?.model_route.reason_model ?? "-"}</strong>
          </div>
          {props.response?.warnings.map((warning) => (
            <div key={warning} className="border border-amber-300 bg-amber-50 p-2 text-amber-800">
              {warning}
            </div>
          ))}
        </div>
      </aside>

      <section className="textbook-panel p-3">
        <div className="mb-3 flex items-center justify-between border-b border-neutral-300 pb-2">
          <span className="font-extrabold">板书步骤</span>
          <span className="text-sm text-neutral-600">
            {activeStep ? `Step ${activeStep.index} / ${solution?.steps.length}` : "未生成"}
          </span>
        </div>
        {solution ? <StepList steps={solution.steps} activeIndex={props.activeIndex} onStep={props.onStep} /> : null}
        <div className="mt-3 border border-neutral-300 bg-white p-3">
          <div className="mb-2 text-xs font-bold text-neutral-500">公式</div>
          <div className="font-mono leading-7">{activeStep?.formula ?? "生成后显示当前步骤公式。"}</div>
        </div>
        <div className="mt-3 border-l-4 border-neutral-950 bg-neutral-50 p-3 leading-7">
          <strong className="block">为什么这样做？</strong>
          {activeStep?.teacher_explanation ?? "每一步最多 3 句话，解释当前操作的学习意义。"}
        </div>
      </section>

      <section>
        <VisualizationPanel step={activeStep} confirmationRequired={solution?.confirmation_required ?? false} />
      </section>
    </section>
  );
}
