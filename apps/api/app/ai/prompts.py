VISION_EXTRACT_PROMPT = """
You are extracting an engineering problem for a visual learning solver.
Return strict JSON with subject, topic, text, components or matrix values.
If the selected reasoning model cannot see images, include a compact text/netlist bridge.
"""

TEACHER_EXPLAIN_PROMPT = """
Explain why this step is done. Use Chinese. Maximum 3 short sentences.
No motivational filler. Connect the explanation to the current formula or diagram.
"""
