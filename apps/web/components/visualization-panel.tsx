import type { SolutionStep } from "@/lib/types";

export function VisualizationPanel(props: { step?: SolutionStep; confirmationRequired: boolean }) {
  if (!props.step) {
    return (
      <div className="textbook-panel grid min-h-96 place-items-center p-6 text-center text-neutral-500">
        输入题目后，这里会显示每一步对应的 SVG 步骤图。
      </div>
    );
  }

  return (
    <div className="textbook-panel p-3">
      <div className="mb-3 flex items-center justify-between gap-3 text-sm text-neutral-600">
        <span>
          当前图示：Step {props.step.index} {props.step.title}
        </span>
        <span>{props.step.visualization.mode}</span>
      </div>
      <div
        className="safe-svg overflow-hidden border border-neutral-300 bg-white"
        dangerouslySetInnerHTML={{ __html: props.step.visualization.svg }}
      />
      {props.confirmationRequired && props.step.index === 1 ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-neutral-300 pt-3 text-sm text-neutral-600">
          <span>识别后先重画电路图：是这个连接关系吗？</span>
          <button className="border border-neutral-300 bg-white px-3 py-1">是</button>
          <button className="border border-neutral-300 bg-white px-3 py-1">不是，重新识别</button>
        </div>
      ) : null}
    </div>
  );
}
