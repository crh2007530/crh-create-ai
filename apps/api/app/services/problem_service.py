from uuid import uuid4

from app.ai.gateway import AIGateway
from app.core.config import Settings
from app.parsers.registry import build_parser_registry
from app.parsers.topic_classifier import classify_topic
from app.schemas.problem_document import ProblemDocument
from app.schemas.solution import ModelPreference, Problem, Solution, Subject
from app.schemas.visual_step import VisualSolution
from app.schemas.math_result import MathResult
from app.schemas.validation_result import ValidationResult
from app.services.math_adapter import MathAdapter
from app.services.topic_solver_adapter import TopicSolverAdapter
from app.services.validation_adapter import ValidationAdapter
from app.services.visual_solution_adapter import visual_solution_to_legacy_steps


def classify_subject(question: str, requested: Subject) -> str:
    if requested != Subject.auto:
        return "linear_algebra" if requested == Subject.linear_algebra else "circuit"
    classification = classify_topic(question)
    if classification.domain == "linear_algebra":
        return "linear_algebra"
    if classification.domain == "circuit":
        return "circuit"
    return "circuit"


def parse_problem_document(question: str, subject: Subject) -> ProblemDocument:
    try:
        registry = build_parser_registry()
        document = registry.parse(question)
        if subject != Subject.auto and document.domain == "generic":
            forced_domain = "linear_algebra" if subject == Subject.linear_algebra else "circuit"
            document.domain = forced_domain
            document.topic = "gaussian_elimination" if forced_domain == "linear_algebra" else "node_voltage"
            document.metadata["forced_subject"] = subject.value
        return document
    except Exception as exc:
        classification = classify_topic(question)
        return ProblemDocument(
            domain=classification.domain,
            topic=classification.topic,
            difficulty=classification.difficulty,
            sourceType="text",
            originalQuestion=question,
            metadata={"parser": "error_fallback", "error": str(exc)},
        )


def solve_math(problem_document: ProblemDocument) -> MathResult | None:
    return MathAdapter().solve(problem_document)


def validate_solution(problem_document: ProblemDocument, math_result: MathResult | None) -> ValidationResult | None:
    return ValidationAdapter().validate(problem_document, math_result)


def solve_by_topic(
    problem_document: ProblemDocument,
    math_result: MathResult | None = None,
    validation_result: ValidationResult | None = None,
) -> VisualSolution:
    return TopicSolverAdapter().solve(problem_document, math_result, validation_result)


async def solve_problem(
    settings: Settings,
    question: str,
    subject: Subject,
    preference: ModelPreference,
    has_file: bool,
) -> tuple[Solution, dict[str, str], list[str]]:
    gateway = AIGateway(settings)
    problem_document = parse_problem_document(question, subject)
    resolved_subject = "linear_algebra" if problem_document.domain == "linear_algebra" else "circuit"
    route = gateway.route(preference, needs_vision=has_file)
    warnings = await gateway.explain_bridge(preference, needs_vision=has_file)

    topic = problem_document.topic if problem_document.topic != "generic" else ("gaussian_elimination" if resolved_subject == "linear_algebra" else "node_voltage")
    if problem_document.topic == "generic":
        problem_document.topic = topic

    math_result = solve_math(problem_document)
    validation_result = validate_solution(problem_document, math_result)
    visual_solution = solve_by_topic(problem_document, math_result, validation_result)
    visual_solution.topic = topic
    visual_solution.difficulty = problem_document.difficulty
    visual_solution.metadata["problem_document_id"] = problem_document.id
    if math_result:
        visual_solution.metadata["math_result_success"] = math_result.success
    if validation_result:
        visual_solution.validation_summary = visual_solution.validation_summary or (
            "Verified" if validation_result.passed else "Partial Verification" if validation_result.score > 0 else "Verification Failed"
        )

    reason_provider = route["reason_provider"]
    if reason_provider != "none":
        provider_visual_solution = await gateway.solve_visual(
            provider_name=reason_provider,
            prompt="Return structured teaching steps for an engineering visual solver.",
            payload={
                "question": question,
                "problem_document": problem_document.model_dump(by_alias=True),
                "math_result": math_result.model_dump() if math_result else None,
                "validation_result": validation_result.model_dump() if validation_result else None,
            },
            model=route["reason_model"],
            topic=topic,
        )
        if provider_visual_solution.steps:
            visual_solution = provider_visual_solution
        else:
            visual_solution.metadata["provider_visual_solution"] = provider_visual_solution.model_dump()

    confirmation_required = resolved_subject == "circuit"
    summary = (
        "线性代数题目已结构化，并由题型 Solver 生成教学步骤。"
        if resolved_subject == "linear_algebra"
        else "电路题目已结构化，并由题型 Solver 生成教学步骤。"
    )

    problem = Problem(
        id=f"problem_{uuid4().hex}",
        input_mode="image" if has_file else "text",
        subject=resolved_subject,
        topic=topic,
        original_text=question or "上传题目图片",
        parsed_payload={
            "mode": "mvp",
            "vision_bridge": has_file and preference.provider.value == "deepseek",
            "problem_document": problem_document.model_dump(by_alias=True),
        },
        model_selection=preference,
    )
    solution = Solution(
        id=f"solution_{uuid4().hex}",
        problem=problem,
        problem_document=problem_document,
        math_result=math_result,
        validation_result=validation_result,
        summary=summary,
        confirmation_required=confirmation_required,
        steps=visual_solution_to_legacy_steps(visual_solution),
        visual_solution=visual_solution,
    )
    return solution, route, warnings
