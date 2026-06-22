from html import escape

from app.schemas.visual_step import VisualStep


COMPONENT_HIGHLIGHTS = {
    "Vs": '<rect x="24" y="102" width="112" height="136" fill="#fff7cc" stroke="#111" stroke-width="1.5"/>',
    "R1": '<rect x="184" y="72" width="118" height="76" fill="#fff7cc" stroke="#111" stroke-width="1.5"/>',
    "R2": '<rect x="336" y="128" width="70" height="142" fill="#fff7cc" stroke="#111" stroke-width="1.5"/>',
    "R3": '<rect x="506" y="128" width="70" height="142" fill="#fff7cc" stroke="#111" stroke-width="1.5"/>',
}

NODE_HIGHLIGHTS = {
    "Node A": '<circle cx="370" cy="110" r="24" fill="#fff7cc" stroke="#111" stroke-width="1.8"/>',
    "Node B": '<circle cx="540" cy="110" r="24" fill="#fff7cc" stroke="#111" stroke-width="1.8"/>',
    "Ground": '<circle cx="370" cy="300" r="24" fill="#fff7cc" stroke="#111" stroke-width="1.8"/>',
}

OVERLAY_TARGETS = {
    "Node A": (342, 72),
    "Node B": (511, 72),
    "Ground": (318, 354),
    "R1": (220, 66),
    "R2": (394, 188),
    "R3": (563, 188),
    "I1": (228, 40),
    "I2": (416, 192),
    "I3": (586, 192),
}


def _visible(flag: bool) -> str:
    return "1" if flag else "0"


def _highlight_svg(step: VisualStep) -> str:
    parts: list[str] = []
    for highlight in step.highlights:
        if highlight.type == "component":
            parts.append(COMPONENT_HIGHLIGHTS.get(highlight.target, ""))
        if highlight.type == "node":
            parts.append(NODE_HIGHLIGHTS.get(highlight.target, ""))
    return "".join(parts)


def _annotation_svg(step: VisualStep) -> str:
    if not step.annotations:
        return ""
    lines = []
    y = 446
    for annotation in step.annotations[:3]:
        label = escape(annotation.label)
        lines.append(f'<text x="26" y="{y}" class="note">- {label}</text>')
        y += 18
    return "".join(lines)


def _overlay_svg(step: VisualStep) -> str:
    parts = []
    for overlay in step.overlays:
        x = overlay.x
        y = overlay.y
        if (x is None or y is None) and overlay.target in OVERLAY_TARGETS:
            x, y = OVERLAY_TARGETS[overlay.target]
        if x is None or y is None:
            continue
        text = escape(overlay.text or overlay.target or "")
        parts.append(
            f'<g><rect x="{x - 6}" y="{y - 18}" width="{max(46, len(text) * 8)}" height="22" '
            f'fill="#fff" stroke="#111"/><text x="{x}" y="{y - 3}" class="small">{text}</text></g>'
        )
    return "".join(parts)


def render_circuit_step_svg(step: VisualStep) -> str:
    mode = str(step.metadata.get("render_mode", "base"))
    show_nodes = mode in {"nodes", "equation", "result"}
    show_current = mode in {"current", "equation", "result"}
    show_equation = mode == "equation"
    show_result = mode == "result"
    title = escape(step.title)
    formula = escape(step.formula or "")
    explanation = escape(step.explanation)
    highlights = _highlight_svg(step)
    annotations = _annotation_svg(step)
    overlays = _overlay_svg(step)

    return f"""
<svg viewBox="0 0 620 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="circuit teaching step">
  <rect width="620" height="500" fill="#fff"/>
  <defs>
    <marker id="arrowHead" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#111"/>
    </marker>
    <style>
      .wire,.component,.ground,.arrow {{ stroke:#111; stroke-width:2.4; fill:none; stroke-linecap:square; stroke-linejoin:miter; }}
      .text {{ fill:#111; font:700 14px Arial,sans-serif; }}
      .small {{ fill:#111; font:600 12px Arial,sans-serif; }}
      .note {{ fill:#111; font:600 13px Arial,sans-serif; }}
      .title {{ fill:#111; font:800 18px Arial,sans-serif; }}
      .node {{ fill:#111; }}
      .nodeRing {{ fill:#fff; stroke:#111; stroke-width:2.2; opacity:{_visible(show_nodes)}; }}
      .current {{ opacity:{_visible(show_current)}; }}
      .equation {{ opacity:{_visible(show_equation)}; }}
      .result {{ opacity:{_visible(show_result)}; }}
      .kcl {{ stroke-width:{'4' if show_equation else '2.4'}; }}
    </style>
  </defs>

  <rect x="14" y="12" width="592" height="36" fill="#f7f7f7" stroke="#111"/>
  <text x="26" y="36" class="title">{title}</text>

  <g transform="translate(0 54)">
    {highlights}
    <path class="wire" d="M80 110 H190"/>
    <path class="wire kcl" d="M260 110 H370"/>
    <path class="wire kcl" d="M440 110 H540"/>
    <path class="wire" d="M80 300 H540"/>
    <path class="wire kcl" d="M370 110 V300"/>
    <path class="wire kcl" d="M540 110 V300"/>
    <path class="wire" d="M80 110 V142"/>
    <path class="wire" d="M80 238 V300"/>

    <circle cx="80" cy="190" r="48" fill="#fff" stroke="#111" stroke-width="2.4"/>
    <text class="text" x="60" y="194">Vs</text>
    <text class="small" x="50" y="258">18V</text>
    <text class="text current" x="64" y="139">+</text>
    <text class="text current" x="67" y="254">-</text>

    <path class="component" d="M190 110 h14 l8 -16 l16 32 l16 -32 l16 32 l16 -32 l8 16 h14"/>
    <text class="small" x="220" y="78">R1 2Ω</text>
    <path class="component" d="M370 142 v12 l-16 8 l32 16 l-32 16 l32 16 l-32 16 l16 8 v12"/>
    <text class="small" x="394" y="198">R2 4Ω</text>
    <path class="component" d="M540 142 v12 l-16 8 l32 16 l-32 16 l32 16 l-32 16 l16 8 v12"/>
    <text class="small" x="563" y="198">R3 8Ω</text>

    <circle class="nodeRing" cx="370" cy="110" r="18"/>
    <circle class="nodeRing" cx="540" cy="110" r="18"/>
    <circle class="nodeRing" cx="370" cy="300" r="18"/>
    <circle class="node" cx="370" cy="110" r="4"/>
    <circle class="node" cx="540" cy="110" r="4"/>
    <circle class="node" cx="370" cy="300" r="4"/>
    <text class="text" x="342" y="82">Node A</text>
    <text class="text" x="511" y="82">Node B</text>
    <path class="ground" d="M338 300 h64 M350 314 h40 M362 328 h16"/>
    <text class="small" x="318" y="354">Ground</text>

    <g class="current">
      <path class="arrow" marker-end="url(#arrowHead)" d="M170 62 H300"/>
      <text class="small" x="228" y="50">I1</text>
      <path class="arrow" marker-end="url(#arrowHead)" d="M405 148 V248"/>
      <text class="small" x="416" y="202">I2</text>
      <path class="arrow" marker-end="url(#arrowHead)" d="M575 148 V248"/>
      <text class="small" x="586" y="202">I3</text>
    </g>

    <g class="equation">
      <rect x="88" y="22" width="420" height="34" fill="#fff" stroke="#111"/>
      <text class="small" x="101" y="44">(18 - VA)/R1 = VA/R2 + VB/R3</text>
    </g>

    <g class="result">
      <rect x="88" y="22" width="446" height="58" fill="#fff" stroke="#111"/>
      <text class="small" x="101" y="44">VA = 12V, VB = 12V, I1 = 3A, I2 = 3A</text>
      <text class="small" x="101" y="64">Pmax = 18W, Q = 0var, S = 36VA</text>
    </g>
    {overlays}
  </g>

  <rect x="14" y="424" width="592" height="62" fill="#fff" stroke="#111"/>
  <text x="26" y="444" class="note">公式：{formula}</text>
  <text x="26" y="466" class="note">说明：{explanation}</text>
  {annotations}
</svg>
""".strip()


def render_circuit_svg(mode: str) -> str:
    step = VisualStep(
        id="legacy_circuit_step",
        title="电路步骤图",
        explanation="教材风格电路图。",
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
        overlays=[
            {"target": "Node A", "text": "Node A"},
            {"target": "Node B", "text": "Node B"},
        ],
    )
    return render_circuit_step_svg(step)
