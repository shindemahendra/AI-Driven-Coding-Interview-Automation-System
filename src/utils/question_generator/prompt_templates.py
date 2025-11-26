# src/utils/question_generator/prompt_templates.py

MCQ_PROMPT = """
Generate exactly {count} UNIQUE, professional-grade MCQ questions for {round_name}.

DIFFICULTY LEVEL (VERY IMPORTANT):
- "easy"    → Should target freshers (0–2 years experience)
              Focus on fundamentals, basics, direct concepts.
- "medium"  → Should target experienced engineers (3–9 years)
              Include deeper logic, real-world coding concepts, intermediate DS.
- "hard"    → Should target senior engineers (10+ years)
              Include advanced reasoning, complex debugging, deeper Python internals,
              design thinking, and high-level problem solving.

ROUND DEFINITIONS:
L1 - Logical Puzzles:
    - easy   → basic logical reasoning & patterns (fresher-level aptitude)
    - medium → structured puzzles requiring multi-step deduction
    - hard   → complex constraint-based puzzles (consulting-style)

L2 - Syntax & Data Structures MCQs:
    - easy   → basic Python syntax, lists, dicts, loops, if/else
    - medium → decorators, generators, OOP, comprehension, complexity
    - hard   → concurrency, async, memory model, deep DS concepts

L3 - Debugging (Buggy Code MCQs):
    - easy   → simple bugs (typos, indentation, basic logical errors)
    - medium → mutation bugs, off-by-one, DS misuse, edge cases
    - hard   → race conditions, shadowing, scoping, generator misuse

L5 - Soft Skills (Situational MCQs):
    - easy   → simple scenarios for freshers (communication, following instructions)
    - medium → cross-team communication, estimation, minor conflict handling
    - hard   → leadership, decision making, managing crises or blockers

STRICT REQUIREMENTS:
- EXACTLY 4 options: A, B, C, D
- EXACT MATCH to JSON schema
- NO explanations, NO markdown
- JSON ONLY

JSON Format:
[
  {{
    "question": "",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "A",
    "topic": "",
    "difficulty": "{difficulty}"
  }}
]
"""

CODING_PROMPT = """
Generate exactly 1 professional coding problem for round L4.

DIFFICULTY LEVEL (IMPORTANT):
- "easy"    → fresher-level coding, simple arrays/strings problems
- "medium"  → professional mid-level engineering problems (DS, algorithms, data parsing)
- "hard"    → senior-level challenges (dynamic programming, greedy, BFS/DFS variants, multi-step logic)

IT-INDUSTRY STYLE (MANDATORY):
- Must feel like a real HackerRank / Codility / LeetCode problem
- Realistic business or engineering scenario
- Clear constraints & edge cases
- No childish or academic-only examples

STRICT JSON Format:
{{
  "title": "",
  "description": "",
  "input_format": "",
  "output_format": "",
  "constraints": "",
  "sample_input": "",
  "sample_output": "",
  "difficulty": "{difficulty}"
}}
"""
