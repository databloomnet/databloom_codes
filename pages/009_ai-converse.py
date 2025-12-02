# wikipedia-playground.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os
import wikipedia

from rate_limiter import RateLimiter
from openai import OpenAI
import anthropic
from response_parser import get_response_summary

LLM_INPUT_CHAR_LIMIT = 2000

st.set_page_config(page_title="AI Converse", page_icon="💬")


load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Conversation history in session_state
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # list of dicts: {time, model_label, question, answer}


MODEL_OPTIONS = [
    {
        "label": "OpenAI – gpt-5 mini",
        "provider": "openai",
        "model": "gpt-5-mini",
    },
    {
        "label": "OpenAI – gpt-5 nano",
        "provider": "openai",
        "model": "gpt-5-nano",
    },
    {
        "label": "Anthropic: Sonnet 3.5",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
    },
    {
        "label": "Anthropic: Haiku 4.5",
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
    },
]




# <rate limiter init>
if  "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=5,interval_sec=300)


st.title("AI Converse 🤖💬")
st.write(
    "Select a model, type a message, and I’ll send it to that LLM and show the reply."
)



# choose model
model_labels = [m["label"] for m in MODEL_OPTIONS]
selected_label = st.selectbox("Choose model", model_labels, index=0)

selected_cfg = next(m for m in MODEL_OPTIONS if m["label"] == selected_label)
provider = selected_cfg["provider"]
model_name = selected_cfg["model"]

st.caption(f"Using **{provider}** / **{model_name}**")



# message
with st.form("chat_form"):
    user_text = st.text_area(
        "Your message",
        value="Say hello and tell me a fun fact.",
        height=12,
    )
    submitted = st.form_submit_button("Send")

# ---------- Helpers ----------

def call_openai_chat(model: str, message: str) -> tuple[str, dict | None]:
    """
    Returns (reply_text, usage_dict_or_None)
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=OPENAI_API_KEY)

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )

    reply = resp.choices[0].message.content
    usage = getattr(resp, "usage", None)
    # usage might have .total_tokens, .prompt_tokens, etc.
    usage_dict = usage.model_dump() if usage is not None else None
    return reply, usage_dict


def call_anthropic_chat(model: str, message: str) -> tuple[str, dict | None]:
    """
    Returns (reply_text, usage_dict_or_None)
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    resp = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[
            {"role": "user", "content": message},
        ],
    )

    # Anthropic's content is a list of blocks; simplest is first text block
    if resp.content and resp.content[0].type == "text":
        reply = resp.content[0].text
    else:
        reply = "<no text content>"

    usage = getattr(resp, "usage", None)
    # usage has input_tokens, output_tokens, etc.
    usage_dict = usage.model_dump() if usage is not None else None
    return reply, usage_dict


# ---------- Handle submit ----------

if submitted:
    if not user_text.strip():
        st.warning("Please type a message before sending.")
        st.stop()

    # Basic key validation before we spin up the spinners
    if provider == "openai" and not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY is missing. Check your environment.")
        st.stop()
    if provider == "anthropic" and not ANTHROPIC_API_KEY:
        st.error("ANTHROPIC_API_KEY is missing. Check your environment.")
        st.stop()

    with st.spinner(f"Talking to {provider} ({model_name})..."):
        t0 = time.time()
        try:
            if provider == "openai":
                reply, usage = call_openai_chat(model_name, user_text)
            elif provider == "anthropic":
                reply, usage = call_anthropic_chat(model_name, user_text)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            st.error(f"Error calling {provider}: {e}")
            st.stop()
        t1 = time.time()

    st.success(f"Response received in {t1 - t0:0.2f} seconds.")

    st.markdown("### Model reply")
    # auto-height-ish: use a small height; Streamlit will add scroll if needed
    st.text_area(" ", value=reply, height=200)

    # Optional: show token usage if available
    if usage:
        with st.expander("Token / usage details"):
            st.json(usage)

st.markdown(
    "[view code](https://github.com/databloomnet/databloom_codes/blob/main/pages/007_ai_converse.py)"
)

