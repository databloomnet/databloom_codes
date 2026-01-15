# chatting.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os

from rate_limiter import RateLimiter

from openai import OpenAI
import anthropic

MAX_TOKENS = 500


# -------------------------
# API keys
# -------------------------
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


# -------------------------
# Rate Limiter
# -------------------------
if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=10,interval_sec=300)

# -------------------------
# chat helpers
# -------------------------

def chat_with_llm(model, question, history):
    if model.startswith("gpt"):
        return chat_with_gpt(model, question, history)
    elif model.startswith("claude"):
        return chat_with_anthropic(model, question, history)
    else:
        print("error - model not recognized")
        return




# return response, but may be ignored
def chat_with_gpt(model, question, history):
    new_history=[
        { "role": m["role"], "content": m["content"] }
        for m in history
    ]
    new_history.append({"role": "user", "content": question})


    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens = MAX_TOKENS * 100,
        messages = new_history
        # messages=[
        #     {"role": "user", "content": question},
        # ],
    )

    answer = response.choices[0].message.content
    return answer, response


def chat_with_anthropic(model, question, history):
    new_history=[
        { "role": m["role"], "content": m["content"] }
        for m in history
    ]
    new_history.append({"role": "user", "content": question})


    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=model,
        max_tokens = MAX_TOKENS,
        # messages=[
        #     {"role": "user", "content": question},
        # ],
        messages = new_history,
    )

    if response.content and response.content[0].type == "text":
        answer = response.content[0].text
    else:
        answer = "<no text content>"
    return answer, response
