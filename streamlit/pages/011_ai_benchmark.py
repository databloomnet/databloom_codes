# 011_ai_benchmark.py

import streamlit as st
import time
import json
import os
import re
from chatting import chat_with_llm

# -------------------------
# Constants
# -------------------------

PROMPT = """
You must solve the problem carefully.

IMPORTANT:
- The first character in your response must be the letter that is your answer.
- If you can, you should add a probability percentage representing your confidence in your answer
- Example Reply: "A 80%" means "I choose answer A and I'm 80% confident in that reply"
- Example Reply: "E 100%" means "I choose answer E and I'm 100% confident in that reply"
- You may, but are not required, to provide a brief explanation as to how and why you chose your response.  This should be on a new line.

Problem:
{PUZZLE_TEXT}

"""

MODEL_LIST = [
    "gpt-5-mini",
    "gpt-5-nano",
    "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5-20251001",
]

# -------------------------
# Load problems
# -------------------------

_problems_path = os.path.join(os.path.dirname(__file__), "..", "benchmark_problems.json")
with open(_problems_path) as f:
    _problems_data = json.load(f)

PROBLEMS = {p["id"]: p for p in _problems_data["problems"]}
PROBLEM_IDS = [p["id"] for p in _problems_data["problems"]]

# -------------------------
# Session state
# -------------------------

if "benchmark_history" not in st.session_state:
    st.session_state.benchmark_history = []

# -------------------------
# Helper functions
# -------------------------

def parse_llm_answer(response_text):
    """Extract answer letter and confidence from LLM response."""
    text = response_text.strip()
    answer = text[0].upper() if text else ""
    confidence = None
    match = re.search(r'(\d+)\s*%', text.split('\n')[0])
    if match:
        confidence = int(match.group(1))
    return answer, confidence


def solve_problem(model, problem):
    """Run a single benchmark problem. Returns a result dict."""
    formatted_prompt = PROMPT.replace("{PUZZLE_TEXT}", problem["prompt"])

    start = time.time()
    answer_text, _response = chat_with_llm(model, formatted_prompt, [])
    latency = round(time.time() - start, 2)

    llm_answer, confidence = parse_llm_answer(answer_text)
    is_correct = llm_answer == problem["correct_answer"]

    return {
        "model": model,
        "problem_id": problem["id"],
        "difficulty": problem["difficulty"],
        "category": problem["category"],
        "correct_answer": problem["correct_answer"],
        "llm_answer": llm_answer,
        "confidence": confidence,
        "is_correct": is_correct,
        "latency": latency,
        "full_response": answer_text,
    }


# -------------------------
# Main UI
# -------------------------

st.title("AI Benchmark")
st.markdown(
    "Select a model and a logic problem, then press **Solve** to see how the LLM performs. "
    "Use **Run All** to benchmark the selected model against every problem."
)

# --- Model & Problem selection ---
model = st.selectbox("Choose a model", MODEL_LIST)
problem_id = st.selectbox("Choose a problem", PROBLEM_IDS)

selected_problem = PROBLEMS[problem_id]

with st.container(border=True):
    st.markdown(f"**Difficulty:** {selected_problem['difficulty']}  &nbsp;|&nbsp;  **Category:** {selected_problem['category']}")
    st.markdown(f"**Answer format:** {selected_problem['answer_format']}  &nbsp;|&nbsp;  **Correct answer:** {selected_problem['correct_answer']}")
    st.text(selected_problem["prompt"])

# --- Action buttons ---
col_solve, col_run_all = st.columns(2)

with col_solve:
    solve_clicked = st.button("Solve", use_container_width=True)

with col_run_all:
    run_all_clicked = st.button("Run All", use_container_width=True)

# --- Solve single problem ---
if solve_clicked:
    if not st.session_state.rate_limiter.allow():
        st.error("Rate limited. " + st.session_state.rate_limiter.status(verbose=True))
        st.stop()

    with st.spinner(f"Solving {problem_id} with {model}..."):
        result = solve_problem(model, selected_problem)

    st.session_state.benchmark_history.append(result)
    if result["is_correct"]:
        st.toast(f"Correct! ({result['latency']}s)", icon="✅")
    else:
        st.toast(f"Incorrect — answered {result['llm_answer']}, expected {result['correct_answer']} ({result['latency']}s)", icon="❌")
    st.rerun()

# --- Run All problems ---
if run_all_clicked:
    num_problems = len(PROBLEM_IDS)
    correct_count = 0

    with st.status(f"Running all {num_problems} problems with {model}...", expanded=True) as status:
        for i, pid in enumerate(PROBLEM_IDS):
            if not st.session_state.rate_limiter.allow():
                st.error("Rate limited. " + st.session_state.rate_limiter.status(verbose=True))
                st.stop()

            st.write(f"Solving problem {i + 1}/{num_problems}: **{pid}**...")
            result = solve_problem(model, PROBLEMS[pid])
            st.session_state.benchmark_history.append(result)

            mark = "✅" if result["is_correct"] else "❌"
            st.write(f"  {mark} {pid} — answered {result['llm_answer']} ({result['latency']}s)")
            if result["is_correct"]:
                correct_count += 1

        status.update(label=f"Done — {model} scored {correct_count}/{num_problems}", state="complete")
    st.rerun()

# -------------------------
# History / Scorecard
# -------------------------

st.subheader("History")

history = st.session_state.benchmark_history
if history:
    total = len(history)
    correct = sum(1 for r in history if r["is_correct"])
    st.markdown(f"**{correct}** correct out of **{total}** total")

    for i, r in enumerate(reversed(history)):
        mark = "✅" if r["is_correct"] else "❌"
        conf_str = f" — {r['confidence']}% confidence" if r["confidence"] is not None else ""
        label = f"{mark} {r['model']}  |  {r['problem_id']}  |  diff {r['difficulty']}  |  answered {r['llm_answer']}{conf_str}  |  {r['latency']}s"
        with st.expander(label):
            st.markdown(f"**Correct answer:** {r['correct_answer']}")
            st.text(r["full_response"])

    if st.button("Clear History"):
        st.session_state.benchmark_history = []
        st.rerun()
else:
    st.caption("No results yet — press Solve or Run All above.")

# -------------------------
# GitHub link
# -------------------------
st.divider()
st.markdown(
    "[code on github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/011_ai_benchmark.py)"
)
