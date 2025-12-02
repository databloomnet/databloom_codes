# 005_ai01.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os

from rate_limiter import RateLimiter
#from model_calls import is_prompt_scary
from openai import OpenAI

def toy_is_prompt_scary(msg: str):
    """
    simple example
    returns True if it finds a banned word
    """
    BANNED_WORDS = ["kill","murder"]
    m = msg.strip()
    return any(banned_word in m.lower() for banned_word in BANNED_WORDS)


if  "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=2,interval_sec=60)

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
#anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')


if not openai_api_key:
    st.error("OPENAI_API_KEY is not set. Please configure your environment.")
    st.stop()



st.title("Hello, ChatGPT")

model="gpt-4.1-nano"
#msg = "Claude, by anthropic, is one of the most famous foundation models.  Go ahead and ask Claude a question."
msg = f"ChatGPT, by OpenAI, is probably the most famous company with foundation models.  They have many models, let's try {model}."
msg += " We use two statements for this.  First we setup a connection with OpenAI and then we send a request and assign it to response."
msg += " I'll add some timers to the code so we can see how long stuff can take.  I'll explain the 2nd to last line shortly."
msg += " (fyi: As this is running in streamlit this isn't the full code.  You can see all the code on the github page (at bottom).)"

st.markdown(msg)

msg_code = """
t0 = time.time()
openai = OpenAI()
t1 = time.time()
response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[{"role": "user", "content": user_text}],
)
t2 = time.time()
answer = response.choices[0].message.content
print(answer)
"""
st.code(msg_code, line_numbers=True)

MAX_CHARS = 50

with st.form("single_form"):
    user_text = st.text_area(
        "Your question",
        max_chars=MAX_CHARS,
        value="In 25 words or less, what is AI?",
        help=f"Up to {MAX_CHARS} characters.",
    )

    submitted = st.form_submit_button("Submit")

if submitted:
    # check rate limiter
    if not st.session_state.rate_limiter.allow():
        #print("rate limited")
        st.error("Oops, I'm rate limited.  Please wait a bit and try again.   " + st.session_state.rate_limiter.status(verbose=True))
        st.stop()


    # 1. Basic sanity check
    if toy_is_prompt_scary(user_text):
        st.error("Input rejected by sanity check. Try something else.")
        st.stop()

    # 2. Call model with spinner + timing
    with st.spinner("Thinking..."):
        st.write("Establishing connection...")
        t0 = time.time()
        openai = OpenAI()
        t1 = time.time()
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": user_text}],
                #max_output_tokens = 50
                max_tokens = 50
            )
        except Exception as e:
            st.error(f"Model call failed: {e}")
            st.stop()

    t2 = time.time()
    m = f"We received a response from OpenAI.  It took {t1 - t0:4.2f} s to establish a connection and {t2 - t1:4.2f} s to get the response."
    m += "  \nLike most APIs, it returned an object, which includes a lot of stuff we may not want to look at right now."
    m += "  In line 9 we pull out one part of the full response object and print it on line 10"
    st.success(m)
    answer = response.choices[0].message.content

    with st.container():
        st.markdown("### ChatGPT replied with:")
        st.text_area(" ", answer)#, height=1)

    st.markdown(f"You can see the entire object returned below, and/or the full streamlit code on github.  Note the github has some other stuff, like toy_is_prompt_scary() to verify the prompt is sfw and rate limiting so I don't go broke if hackers discover this" )


    with st.container():
        st.markdown("### Here is the entire object it sent (response.model_dump())")
        
        #print(response)
        #st.text_area(" ", "glah")#, height=1)
        st.json(response.model_dump()) # already a pydantic model



    #st.markdown(f"Next up: try asking about a different topic.  Or a different question.  Hopefully something short and easy as I'm paying OpenAi for this, and {model} is cool but not a powerhouse of a model.  Maybe ask about chess?  Or heavy water?")



st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/pages/005_ai-hello.py)")
