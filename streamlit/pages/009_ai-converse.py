# ai-converse.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os

from rate_limiter import RateLimiter
from openai import OpenAI
import anthropic
from response_parser import get_response_summary
from chatting import chat_with_gpt, chat_with_anthropic

# -------------------------
# constants
# -------------------------
MODEL_LIST = [
        "gpt-4o-mini",            # .15
        "gpt-5-mini",             # .25 input
        "gpt-5-nano",             # .05 input
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
]

MAX_TOKENS = 500
DEFAULT_MODEL_INDEX = 4

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
# Session state init
# -------------------------
if "conversation" not in st.session_state:
    # Each item: {"role": "user"|"assistant", "content": str}
    st.session_state.conversation = []

if "model" not in st.session_state:
    st.session_state.model = MODEL_LIST[DEFAULT_MODEL_INDEX]

if "model_index" not in st.session_state:
    st.session_state.model_index = DEFAULT_MODEL_INDEX

if "chat_locked" not in st.session_state:
    # True once the first message is sent (locks model selection)
    st.session_state.chat_locked = False

# -------------------------
# Sidebar: model selection & reset
# -------------------------
with st.sidebar:
    st.header("Chat settings")

    # Disable selection after first message to avoid midstream changes
    disabled = st.session_state.chat_locked


    model = st.selectbox("Choose model:", 
        options = MODEL_LIST,
        index = st.session_state.model_index,
        disabled = disabled,
        help = "select a model to converse with",
    )
    # print("model:", model)
    st.session_state.model = model
    st.session_state.model_index = MODEL_LIST.index(model)

    if st.button("Reset conversation", type="secondary"):
        st.session_state.conversation = []
        st.session_state.model_index = DEFAULT_MODEL_INDEX
        st.session_state.model = MODEL_LIST[DEFAULT_MODEL_INDEX]
        st.session_state.chat_locked = False
        st.rerun()

# -------------------------
# Main UI
# -------------------------
st.title("AI Converse")
st.markdown("Chat with your selected LLM.  It will remember stuff while on this page.")
st.caption(f"**Using model:** `{st.session_state.model}`")

# # Display conversation so far
# for msg in st.session_state.conversation:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# Chat input (only active once a model is chosen)

# with st.container():
#     user_input = st.chat_input(
#         "Type your message...2",
#         disabled=(st.session_state.model is None),
#     )
    # st.text_input("Type your message", key="user_input")
    #st.markdown("[code](https://github.com/databloomnet/databloom_codes/blob/main/pages/009_ai-converse.py)")

# st.write(
#     "[code_on_github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/009_ai-converse.py)"
# )


# -------------------------
# once user input received
# -------------------------

# if user_input:
#     # Lock model for this conversation once first message is sent
#     st.session_state.chat_locked = True
#     model = st.session_state.model

#     #print(f"127: {model}")
#     # 1. Add user message to history and show it
#     st.session_state.conversation.append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     # 2. Call the model with full history

#     # print("user_input...")
#     # print(st.session_state.model, st.session_state.model_index, st.session_state.chat_locked)
#     # print(len(st.session_state.conversation))
#     # for x in st.session_state.conversation:
#     #     print(x)
#     # print("...")


#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             t0 = time.time()

#             if model.startswith("gpt"):
#                 answer, response = chat_with_gpt(model, user_input, st.session_state.conversation)
#                 # answer = response.choices[0].message.content
#             elif model.startswith("claude"):
#                 answer, response = chat_with_anthropic(model, user_input, st.session_state.conversation)
#                 # answer = response.choices[0].message.content
#             else:
#                 st.error("unknown model")
#                 st.stop()

#             st.markdown(answer)
#             st.caption(f"_Response time: {time.time() - t0:0.2f} seconds_")


#                     # {"role": m["role"], "content": m["content"]}
#                     # for m in st.session_state.messages


#             # response = client.chat.completions.create(
#             #     model=model,
#             #     messages=[
#             #         {"role": m["role"], "content": m["content"]}
#             #         for m in st.session_state.messages
#             #     ],
#             # )
#             # t1 = time.time()

#             # answer = response.choices[0].message.content
#             # st.markdown(answer)
#             # st.caption(f"_Response time: {t1 - t0:0.2f} seconds_")


#     # 3. Append assistant reply to history

#     st.session_state.conversation.append(
#         {"role": "assistant", "content": answer}
#     )

#     # 3. Append assistant reply to history
#     st.session_state.conversation.append(
#         {"role": "assistant", "content": answer}
#     )


# -------------------------
# UI: Collapsible history
# -------------------------
with st.expander("Conversation history", expanded=False):
    if st.session_state.conversation:
        for msg in st.session_state.conversation:
            role = "You" if msg["role"] == "user" else "Assistant"
            st.markdown(f"**{role}:** {msg['content']}")
    else:
        st.caption("nothing here yet...")

# -------------------------
# UI: last answer 
# -------------------------
last_answer = None
for msg in reversed(st.session_state.conversation):
    if msg["role"] == "assistant":
        last_answer = msg["content"]
        break

if last_answer:
    st.markdown("### Last answer")
    st.write(last_answer)

# -------------------------
# UI: input message
# -------------------------
# st.text_input - RETAINS VALUE AFTER RERUN, resulting in looping
# with st.form("chat_form"):
#     user_input = st.text_area(
#         "Your message to the llm",
#         value="Tell me a fun fact",
#         height=10,
#     )
#     submitted = st.form_submit_button("Send")
user_input = st.chat_input(
    placeholder="Ask something… (press Enter to send)",
)


# -------------------------
# UI: process when submitted
# -------------------------
if user_input:

    # content = user_input.strip()
    # if not content:
    #     st.warning("Please type a message before sending.")
    #     st.stop()

    # Rate limiting
    if not st.session_state.rate_limiter.allow():
        st.error(
            "Oops, I'm rate limited. Please wait a bit and try again.  "
            + st.session_state.rate_limiter.status(verbose=True)
        )
        st.stop()

    # Lock model after first user message
    st.session_state.chat_locked = True
    model = st.session_state.model

    st.session_state.conversation.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)



    # # Build messages with full history
    # # Start with previous messages, then append new user msg
    
    # messages = list(st.session_state.conversation)
    # #messages.append({"role": "user", "content": content})

    # Call the model
    # with st.spinner("Thinking..."):
    #     t0 = time.time()


    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            t0 = time.time()

            if model.startswith("gpt"):
                answer, response = chat_with_gpt(model, user_input, st.session_state.conversation)
            elif model.startswith("claude"):
                answer, response = chat_with_anthropic(model, user_input, st.session_state.conversation)
            else:
                st.error("unknown model")
                st.stop()

            st.markdown(answer)
            st.caption(f"_Response time: {time.time() - t0:0.2f} seconds_")

    st.session_state.conversation.append(
        {"role": "assistant", "content": answer}
    )

    # Force a re-run so the "last answer" section updates cleanly
    st.rerun()



st.write("Script reran at", datetime.datetime.now())

# -------------------------
# 4) GitHub link directly under the input
# -------------------------
st.markdown(
    "[code_on_github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/009_ai-converse.py)"
)

# # Handle new user message
# if user_input:
#     # append user message to history
#     st.session_state.conversation.append(
#         {"role": "user", "content": user_input}
#     )
#     # trigger your existing logic that calls the model, etc.
#     st.rerun()



