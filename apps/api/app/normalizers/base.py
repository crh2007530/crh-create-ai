from abc import ABC
from uuid import uuid4

from app.ai.providers.base import ProviderSolveResult
from app.schemas.visual_step import VisualSolution, VisualStep


class BaseNormalizer(ABC):
    provider_name = "base"

    def normalize(self, result: ProviderSolveResult, topic: str | None = None) -> VisualSolution:
        steps = [self._normalize_step(raw_step, index) for index, raw_step in enumerate(result.steps, start=1)]
        return VisualSolution(
            answer=result.answer,
            confidence=result.confidence,
            topic=topic,
            steps=steps,
            metadata={
                "provider": self.provider_name,
                "source_metadata": result.metadata,
            },
        )

    def _normalize_step(self, raw_step: dict, index: int) -> VisualStep:
        return VisualStep(
            id=str(raw_step.get("id") or f"visual_step_{uuid4().hex}"),
            title=str(raw_step.get("title") or f"Step {index}"),
            explanation=str(raw_step.get("explanation") or raw_step.get("teacher_explanation") or ""),
            formula=raw_step.get("formula"),
            svgType=str(raw_step.get("svgType") or raw_step.get("svg_type") or "generic"),
            result=raw_step.get("result"),
            highlights=raw_step.get("highlights") or [],
            annotations=raw_step.get("annotations") or [],
            overlays=raw_step.get("overlays") or [],
            metadata=raw_step.get("metadata") or {},
        )
