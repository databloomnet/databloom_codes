# ai-argue.py

import streamlit as st
import contextlib
import datetime
import os
from dotenv import load_dotenv

import pandas as pd

from rate_limiter import RateLimiter
from ai_argue_core import run_debate
import ai_argue_store

# -------------------------
# constants
# -------------------------

WORD_MAX_J1_DEFAULT = 30
WORD_MAX_A_DEFAULT = 10
WORD_MAX_B_DEFAULT = 25
WORD_MAX_J8_DEFAULT = 100

# -------------------------
# Session state init
# -------------------------

if "parties_defined" not in st.session_state:
    st.session_state.parties_defined = False

if "argument_result" not in st.session_state:
    st.session_state.argument_result = False

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []



if "party_A_word_max" not in st.session_state:
    st.session_state.party_A_word_max = WORD_MAX_A_DEFAULT
if "party_B_word_max" not in st.session_state:
    st.session_state.party_B_word_max = WORD_MAX_B_DEFAULT
if "party_J1_word_max" not in st.session_state:
    st.session_state.party_J1_word_max = WORD_MAX_J1_DEFAULT
if "party_J8_word_max" not in st.session_state:
    st.session_state.party_J8_word_max = WORD_MAX_J8_DEFAULT


PROP_EXAMPLES = [
            "P equals NP",
            "murder is always wrong",
            "the good of the many outweighs the good of the few",
            "democracy is always the best form of government",
            "there is no solution to the trolley problem",
            "Javier is the true hero of Les Miserable",
            ".jpg should be pronuced JAY-feg",
            "time travel is impossible",
]

MODEL_LIST = [
        "gpt-4o-mini",            # .15
        "gpt-5-mini",             # .25 input
        "gpt-5-nano",             # .05 input
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
]

DEFAULT_MODEL_INDEX = 4

SPINNER_TEXT = {
    "guidelines": "J (judge) is thinking about the guidelines...",
    "A": "Round {round_num}: A is thinking...",
    "B": "Round {round_num}: B is thinking...",
    "ruling": "J is deciding...",
}

# Columns shown in Explore results, and the ones offered as filters
FILTER_COLUMNS = ["batch_id", "condition", "model_a", "model_b", "model_j", "winner", "status"]

# -------------------------
# API keys (read by ai_argue_core)
# -------------------------
load_dotenv(override=True)


# -------------------------
# Rate Limiter
# -------------------------
if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=10,interval_sec=300)




# -------------------------
# Main UI
# -------------------------
st.title("AI Argue")
st.markdown("Let's start an argument." "(inspired by [Argument - Monty Python](https://www.youtube.com/watch?v=ohDB5gbtaEQ)")

tab_run, tab_explore, tab_analysis = st.tabs(["Run a debate", "Explore results", "Analysis"])

# The other tabs are filled first, so an st.stop() in "Run a debate" can't blank them.

# -------------------------
# Explore results (curated batch data, read-only)
# -------------------------
with tab_explore:
    df = None
    if os.path.exists(ai_argue_store.CURATED_DB):
        try:
            conn = ai_argue_store.connect_readonly(ai_argue_store.CURATED_DB)
            try:
                df = pd.read_sql_query("SELECT * FROM debates ORDER BY timestamp_utc", conn)
            finally:
                conn.close()
        except Exception as e:
            print(f"ai-argue: could not read {ai_argue_store.CURATED_DB}: {e!r}")

    if df is None or df.empty:
        st.info("No batch results yet. They'll appear here once the first batch has run.")
    else:
        filter_cols = st.columns(len(FILTER_COLUMNS))
        for col, name in zip(filter_cols, FILTER_COLUMNS):
            options = sorted(df[name].dropna().astype(str).unique())
            chosen = col.multiselect(name, options, key=f"filter_{name}")
            if chosen:
                df = df[df[name].astype(str).isin(chosen)]

        st.caption(f"{len(df)} debates")
        st.dataframe(df[ai_argue_store.COLUMNS], hide_index=True)
        st.download_button(
            "Download CSV",
            df[ai_argue_store.COLUMNS].to_csv(index=False),
            file_name="ai_argue_debates.csv",
            mime="text/csv",
        )

# -------------------------
# Analysis
# -------------------------
with tab_analysis:
    st.info("First results coming.")


# -------------------------
# Run a debate
# -------------------------
with tab_run:

    st.markdown("Pick a proposition:")
    proposition= st.radio("Select a proposition:", PROP_EXAMPLES)

    st.markdown("Pick LLMs and word limits for each party")


    col1, col2 = st.columns(2)
    with col1:
        party_A_model = st.selectbox("Select Party A model:", MODEL_LIST, index = DEFAULT_MODEL_INDEX)
        party_B_model = st.selectbox("Select Party B model:", MODEL_LIST, index = DEFAULT_MODEL_INDEX)
        party_J_model = st.selectbox("Select Party J model:", MODEL_LIST, index = DEFAULT_MODEL_INDEX)

    with col2:
        party_A_word_max = st.number_input("Max words A can use per statement", min_value = 5, max_value = 40, key = "party_A_word_max", step = 5)
        party_B_word_max = st.number_input("Max words B can use per statement", min_value = 5, max_value = 40, key = "party_B_word_max", step = 5)
        party_J1_word_max = st.number_input("Max words J can use for guidelines", min_value = 5, max_value = 40, key = "party_J1_word_max", step = 5)
        party_J8_word_max = st.number_input("Max words J can use for final ruling", min_value = 5, max_value = 120, key = "party_J8_word_max", step = 5)


    st.divider()


    # -------------------------
    # Start argument button
    # -------------------------
    start_clicked = st.button("Start the argument 🥊")
    st.caption("Debates run here are logged anonymously for research.")

    if start_clicked:
        # Rate limit check
        if not st.session_state.rate_limiter.allow():
            st.error(
                "Oops, you're rate limited. "
                + st.session_state.rate_limiter.status(verbose=True)
            )
            st.stop()

        st.session_state.party_A = {"model": party_A_model}
        st.session_state.party_B = {"model": party_B_model}
        st.session_state.party_J = {"model": party_J_model}
        st.session_state.parties_defined = True
        st.session_state.proposition = proposition

        # reset history/result
        st.session_state.conversation_history = []
        st.session_state.argument_result = None

        output_area = st.container()
        st.divider()

        @contextlib.contextmanager
        def turn_context(step, round_num):
            if step == "A":
                output_area.markdown(f"### Round {round_num}")
            with output_area:
                with st.spinner(SPINNER_TEXT[step].format(round_num=round_num)):
                    yield

        def on_statement(step, round_num, text):
            if step == "guidelines":
                output_area.markdown("**J (guidelines):** " + text)
            elif step in ("A", "B"):
                output_area.markdown(f"**{step} (round {round_num}):** {text}")
                if step == "B":
                    output_area.divider()
            elif step == "ruling":
                output_area.markdown("### Judge J's decision")
                output_area.write(text)

        print("let's rumble!")
        result = run_debate(
            proposition,
            party_A_model, party_B_model, party_J_model,
            party_A_word_max, party_B_word_max, party_J1_word_max, party_J8_word_max,
            turn_context=turn_context,
            on_statement=on_statement,
        )

        if result["status"] == "error":
            output_area.error("The argument stopped early: a model call failed twice. Please try again.")

        st.session_state.conversation_history = result["conversation_history"]
        st.session_state.argument_result = result["ruling_text"]

        # Anonymous visitor log: only the schema's fields, no IP / session / user agent
        try:
            conn = ai_argue_store.connect(ai_argue_store.WEB_DB, wal=True)
            try:
                ai_argue_store.insert_row(conn, ai_argue_store.make_row(result, source="web"))
            finally:
                conn.close()
        except Exception as e:
            print(f"ai-argue: could not log web run: {e!r}")



    st.divider()
    with st.expander("Full argument transcript", expanded=False):
        if st.session_state.conversation_history:
            for line in st.session_state.conversation_history:
                st.markdown(line)
        else:
            st.caption("No argument yet — press the button above to start.")




    st.write("Script ran at", datetime.datetime.now())

# -------------------------
# 4) GitHub link directly under the input
# -------------------------
st.markdown(
    "[code_on_github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/010_ai-argue.py)"
)
