# ai-ask.py

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

#LLM_INPUT_CHAR_LIMIT = 2000
MAX_TOKENS = 256



load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

MODEL_LIST = [
        "gpt-5-mini",
        "gpt-5-nano",
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
]



# <rate limiter init>
if  "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=10,interval_sec=300)

if "transcript" not in st.session_state:
    st.session_state.transcript = []   # each entry: (model, question, answer)

st.title("AI Ask")
st.write(
    "Select a model, type a message, and I’ll send it to that LLM and show the reply.  No info will be saved between questions.  You can ask the same or different questions of the same or different models.  (max tokens is 250)"
)

# ask form
with st.form("ask_form"):
    model = st.selectbox("Choose a model:", MODEL_LIST)
    question = st.text_input("Your question:", "how would you solve the trolley problem?")
    submitted = st.form_submit_button("Send")


# run query
if submitted and question.strip():
    t0 = time.time()
    with st.spinner("Thinking…"):
        if model.startswith("gpt"):        
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                max_completion_tokens = MAX_TOKENS * 100,
                messages=[
                    {"role": "user", "content": question},
                ],
            )

            answer = response.choices[0].message.content


        elif model.startswith("claude"):
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=model,
                max_tokens = MAX_TOKENS,
                messages=[
                    {"role": "user", "content": question},
                ],
            )

            if response.content and response.content[0].type == "text":
                answer = response.content[0].text
            else:
                answer = "<no text content>"

        else:
            st.error("i don't recognize the model yet")
            st.stop()


        # Append to transcript
        st.session_state.transcript.append(
            {
                "model": model,
                "question": question,
                "answer": answer,
                "latency": time.time() - t0,
                "response": response.model_dump()
            }
        )

# render transcripts

if st.session_state.transcript:
    st.markdown("---")
    st.markdown("### Question Transcript\n")

    i = 0
    last = len(st.session_state.transcript)
    for entry in st.session_state.transcript:
        i += 1
        if i != last:
            with st.expander(f"Entry {i} (toggle)", expanded = False):
                st.markdown(f"**Model:** `{entry['model']}`")
                st.markdown(f"**You:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer']}")
                st.caption(f"_Latency: {entry['latency']:.2f} seconds_")
                with st.expander("response", expanded=False):
                    st.json(entry['response'])

        else:
            with st.expander(f"Entry {i} (toggle)", expanded = True):
                st.markdown(f"**Model:** `{entry['model']}`")
                st.markdown(f"**You:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer']}")
                st.caption(f"_Latency: {entry['latency']:.2f} seconds_")
                with st.expander("response", expanded=False):
                    st.json(entry['response'])
        #st.markdown("---")


# with st.expander("See Raw Wikipedia content (toggle)", expanded=False):
#     m = page_contents_truncated
#     if truncation_message:
#         m = truncation_message + "\n\n" + m
#     st.write(m)





st.markdown(
    "[view code](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/008_ai-ask.py)"
)

