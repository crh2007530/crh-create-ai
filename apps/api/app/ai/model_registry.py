from app.schemas.solution import ModelInfo


MODELS: list[ModelInfo] = [
    ModelInfo(
        provider="openai",
        model="gpt-5",
        label="GPT-5",
        supports_vision=True,
        recommended_for=["vision_extract", "circuit_solve", "matrix_solve"],
    ),
    ModelInfo(
        provider="openai",
        model="gpt-5-mini",
        label="GPT-5 mini",
        supports_vision=True,
        recommended_for=["fast_explain", "problem_parse"],
    ),
    ModelInfo(
        provider="gemini",
        model="gemini-pro",
        label="Gemini Pro",
        supports_vision=True,
        recommended_for=["vision_extract", "problem_parse"],
    ),
    ModelInfo(
        provider="gemini",
        model="gemini-flash",
        label="Gemini Flash",
        supports_vision=True,
        recommended_for=["fast_explain", "economy"],
    ),
    ModelInfo(
        provider="deepseek",
        model="deepseek-reasoner",
        label="DeepSeek Reasoner",
        supports_vision=False,
        recommended_for=["structured_reasoning", "circuit_solve", "matrix_solve"],
    ),
    ModelInfo(
        provider="deepseek",
        model="deepseek-chat",
        label="DeepSeek Chat",
        supports_vision=False,
        recommended_for=["teacher_explain", "economy"],
    ),
]
