import type { SolutionStep } from "@/lib/types";

export function StepList(props: {
  steps: SolutionStep[];
  activeIndex: number;
  onStep: (index: number) => void;
}) {
  return (
    <div className="grid gap-2">
      {props.steps.map((step, index) => {
        const active = index === props.activeIndex;
        return (
          <button
            key={step.id}
            className={[
              "grid grid-cols-[64px_1fr] gap-3 border p-3 text-left",
              active ? "border-neutral-950 bg-neutral-50" : "border-neutral-300 bg-white"
            ].join(" ")}
            onClick={() => props.onStep(index)}
          >
            <span className="font-serif font-black">Step {step.index}</span>
            <span>
              <span className="block font-extrabold">{step.title}</span>
              {active ? (
                <span className="mt-1 block text-sm leading-6 text-neutral-600">{step.teacher_explanation}</span>
              ) : null}
            </span>
          </button>
        );
      })}
    </div>
  );
}
