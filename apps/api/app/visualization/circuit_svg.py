from html import escape

from app.schemas.visual_step import VisualStep


def render_circuit_step_svg(step: VisualStep) -> str:
    mode = str(step.metadata.get("render_mode", "identify"))
    title = escape(step.title)
    goal = escape(str(step.metadata.get("step_goal") or _goal_for_mode(mode)))
    conclusion = escape(str(step.result or step.metadata.get("step_conclusion") or _conclusion_for_mode(mode)))
    formula = escape(step.formula or "")
    annotation = escape(step.annotations[0].label) if step.annotations else ""
    body = _body_for_mode(mode, formula)
    explanation = escape(step.explanation)

    return f"""
<svg viewBox="0 0 390 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">
  <rect width="390" height="560" fill="#fff"/>
  <style>
    .h1 {{ font:800 20px Arial,sans-serif; fill:#111; }}
    .label {{ font:700 14px Arial,sans-serif; fill:#111; }}
    .text {{ font:600 13px Arial,sans-serif; fill:#333; }}
    .tiny {{ font:600 11px Arial,sans-serif; fill:#555; }}
    .wire {{ stroke:#111; stroke-width:3; fill:none; stroke-linecap:round; stroke-linejoin:round; }}
    .muted {{ stroke:#bcbcbc; fill:none; stroke-width:2.2; }}
    .focus {{ stroke:#111; stroke-width:4; fill:none; }}
    .noteBox {{ fill:#f8f8f8; stroke:#111; stroke-width:1.6; }}
  </style>
  <rect x="16" y="16" width="358" height="58" fill="#f7f7f7" stroke="#111"/>
  <text x="28" y="40" class="h1">{title}</text>
  <text x="28" y="62" class="text">本步目标：{goal}</text>

  <g transform="translate(0 92)">
    {body}
  </g>

  <rect x="16" y="432" width="358" height="50" class="noteBox"/>
  <text x="28" y="454" class="label">本步结论</text>
  <text x="28" y="474" class="text">{conclusion}</text>

  <rect x="16" y="494" width="358" height="46" fill="#fff" stroke="#d0d0d0"/>
  <text x="28" y="514" class="tiny">公式：{formula}</text>
  <text x="28" y="532" class="tiny">老师解释：{explanation}</text>
  <text x="28" y="548" class="tiny">{annotation}</text>
</svg>
""".strip()


def _goal_for_mode(mode: str) -> str:
    return {
        "identify": "找出题目要求的量",
        "nodes": "确定分析对象 Node A",
        "current": "建立电流参考方向",
        "equation": "围绕 Node A 写 KCL",
        "result": "把结果标回图中",
    }.get(mode, "看懂当前分析步骤")


def _conclusion_for_mode(mode: str) -> str:
    return {
        "identify": "目标量已锁定，下一步选分析对象。",
        "nodes": "Node A 是主要未知量，下一步标参考方向。",
        "current": "参考方向建立完成，下一步列 KCL。",
        "equation": "KCL 方程已建立，下一步求解。",
        "result": "结果已回到图中，可以检查单位和方向。",
    }.get(mode, "本步完成。")


def _body_for_mode(mode: str, formula: str) -> str:
    if mode == "nodes":
        return _nodes_body()
    if mode == "current":
        return _current_body()
    if mode == "equation":
        return _equation_body(formula)
    if mode == "result":
        return _result_body()
    return _identify_body()


def _identify_body() -> str:
    return """
  <rect x="44" y="42" width="302" height="230" fill="#fff" stroke="#d6d6d6"/>
  <path class="muted" d="M80 92 H185 M245 92 H310 M80 238 H310 M80 92 V238 M310 92 V238"/>
  <path class="muted" d="M185 92 h16 l8 -14 l16 28 l16 -28 l16 28 l8 -14 h18"/>
  <circle cx="196" cy="165" r="56" fill="#fff7cc" stroke="#111" stroke-width="3"/>
  <text x="158" y="158" class="label">题目要求</text>
  <text x="166" y="184" class="h1">求 VA / I</text>
  <path class="wire" d="M196 222 v42"/>
  <text x="118" y="304" class="text">先看题目问什么，不急着算。</text>
"""


def _nodes_body() -> str:
    return """
  <path class="muted" d="M76 140 H144 M246 140 H314 M76 260 H314 M76 140 V260 M314 140 V260"/>
  <circle cx="195" cy="140" r="78" fill="#fff7cc" stroke="#111" stroke-width="4"/>
  <circle cx="195" cy="140" r="7" fill="#111"/>
  <text x="151" y="132" class="h1">Node A</text>
  <text x="137" y="166" class="text">未知节点电压 VA</text>
  <path class="wire" d="M195 218 V286"/>
  <path class="wire" d="M151 286 H239 M166 302 H224 M181 318 H209"/>
  <text x="142" y="348" class="text">其它部分先灰化，只盯住 Node A。</text>
"""


def _current_body() -> str:
    return """
  <circle cx="195" cy="152" r="62" fill="#fff" stroke="#111" stroke-width="3"/>
  <text x="167" y="158" class="h1">Node A</text>
  <path class="wire" d="M70 152 H132 M258 152 H320 M195 214 V300"/>
  <path d="M72 104 H142" stroke="#111" stroke-width="5" marker-end="url(#arrow)"/>
  <text x="91" y="88" class="h1">I1</text>
  <path d="M292 104 V176" stroke="#111" stroke-width="5" marker-end="url(#arrow)"/>
  <text x="306" y="142" class="h1">I2</text>
  <text x="70" y="340" class="text">方向是参考方向，算出负值就说明实际相反。</text>
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>
"""


def _equation_body(formula: str) -> str:
    equation = escape(formula or "I1 + I2 = 0")
    return f"""
  <circle cx="195" cy="118" r="54" fill="#fff7cc" stroke="#111" stroke-width="4"/>
  <text x="168" y="124" class="h1">Node A</text>
  <path class="wire" d="M195 172 V220"/>
  <rect x="40" y="226" width="310" height="88" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="68" y="260" class="h1">KCL</text>
  <text x="68" y="292" class="label">{equation}</text>
  <text x="54" y="350" class="text">这一步只看 Node A，不需要再画完整电路。</text>
"""


def _result_body() -> str:
    return """
  <rect x="44" y="58" width="302" height="236" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="78" y="112" class="label">最终结果</text>
  <text x="78" y="162" class="h1">VA = 6V</text>
  <text x="78" y="210" class="h1">I = 2A</text>
  <text x="78" y="258" class="text">把答案放回图里检查方向和单位。</text>
"""


def render_circuit_svg(mode: str) -> str:
    step = VisualStep(
        id="legacy_circuit_step",
        title="电路教学步骤图",
        explanation="每一步只讲一个知识点。",
        formula="",
        svgType="circuit",
        metadata={"render_mode": mode},
    )
    return render_circuit_step_svg(step)


def render_overlay_svg() -> str:
    step = VisualStep(
        id="legacy_overlay_step",
        title="Overlay 模式",
        explanation="标注直接叠加在原题图上。",
        formula="",
        svgType="circuit",
        metadata={"render_mode": "nodes"},
    )
    return render_circuit_step_svg(step)
