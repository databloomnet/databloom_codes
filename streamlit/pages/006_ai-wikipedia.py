# 006_wikipedia.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os
import wikipedia

from rate_limiter import RateLimiter
from openai import OpenAI

LLM_INPUT_CHAR_LIMIT = 2000

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')


def get_est_response_cost(response, t0 = 0):
    # MOVE THIS FUNCTION TO COMMON HELKPEORS
    pt = response.usage.prompt_tokens
    ct = response.usage.completion_tokens
    tt = response.usage.total_tokens
    re = response.usage.completion_tokens_details.reasoning_tokens
    calc_output = ct - re

    out_num_words = len(response.choices[0].message.content.strip().split())

    out = f"Call returned {out_num_words:,} output words"
    if t0 != 0:
        out += f" and took { time.time() - t0 :.1f} seconds"
    else:
        out += "\n"


    out += f"\nToken Usage: (prompt: {pt:5,d})  (reasoning:  {re:,})  (out-calc: {calc_output:,})"
    out += f"\n             (total:  {tt:5,d})  (completion: {ct:,})"


    price_per_million = 0.05
    est1000cost = tt / (price_per_million * 1000000)
    out += f"\nGiven a cost of ($ {price_per_million} per million tokens), estimated cost to make this call 1000 times is ${est1000cost:.2f}"
    
    #print(out)

    return out



# <rate limiter init>
if  "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=2,interval_sec=60)


# store results for reruns
if "summary" not in st.session_state:
    st.session_state.summary = None
if "summary_completion" not in st.session_state:
    st.session_state.summary_completion = None
if "summary_completion_report" not in st.session_state:
    st.session_state.summary_completion_report = None

if "haiku" not in st.session_state:
    st.session_state.haiku = None
if "haiku_completion" not in st.session_state:
    st.session_state.haiku_completion = None
if "haiku_completion_report" not in st.session_state:
    st.session_state.haiku_completion_report = None

if "limerick" not in st.session_state:
    st.session_state.limerick = None
if "limerick_completion" not in st.session_state:
    st.session_state.limerick_completion = None
if "limerick_completion_report" not in st.session_state:
    st.session_state.limerick_completion_report = None
# .



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# <main>
st.title("Wikipedia → ChatGPT Summarizer") # title page

#model="gpt-4.1-nano" # max_tokens
model="gpt-5-nano" # max_completion_tokens



st.write("Using an llm with wikipedia.")
with st.expander("streamlit note (toggle)", expanded=False):
    m = "Fyi I'm learning streamlit and UX patterns as I do this.  This is an interesting bit of UX as first you enter the search term, then you select the word, then you execute one of the queries.  I converted this from the first pattern to the second:"
    st.write(m)
    
    st.code("[[click to show X] and [click to show Y]]") 
    st.code("[[[click to generate X] and [click to generate Y]] \n  # followed by\n[[show X if avail] and [show Y if avail]]]")



# 1. get query topic
query = st.text_input("Search Wikipedia for:", placeholder="e.g. cookie, cloud, castle", max_chars = 30)

if st.button("Reset state"):
    st.session_state.summary = None
    st.session_state.summary_completion = None
    st.session_state.summary_completion_report = None

    st.session_state.haiku = None
    st.session_state.haiku_completion = None
    st.session_state.haiku_completion_report = None

    st.session_state.limerick = None
    st.session_state.limerick_completion = None
    st.session_state.limerick_completion_report = None


if not query:
    st.stop()

# 2) do wikipedia.search
try:
    results = wikipedia.search(query)
except Exception as e:
    st.error(f"Error searching Wikipedia: {e}")
    st.stop()

if not results:
    st.warning("No results found.  Try again.")
    st.stop()

# 3) display results from wikipedia search, ask user to click on one

st.write("Wikipedia found the following entries.  Select one of the below.  Note the \"ambigious\" links don't work - just choose another one")

selected_title = st.radio("Select a result:", results)

if not selected_title:
    st.stop()

# 4) display raw output from this entry
try:
    page = wikipedia.page(selected_title, auto_suggest = False) # need auto_suggest because wikipedia will often deviate to more common requests
except wikipedia.exceptions.DisambiguationError as e:
    st.error("That term is ambiguous. Try picking a more specific result.")
    st.write(e.options)
    st.stop()
except wikipedia.exceptions.PageError:
    st.error("Wikipedia page not found.")
    st.stop()


st.markdown(f"Selection: *{page.title}* at {page.url}")

# truncate as needed
page_contents_truncated = page.content[0:LLM_INPUT_CHAR_LIMIT] + "..."

truncation_message = ""
if len(page.content) > LLM_INPUT_CHAR_LIMIT:
    truncation_message += f"**Wikipedia page truncated from {len(page.content):,} to {LLM_INPUT_CHAR_LIMIT:,} chars**"



# collabsable raw content
with st.expander("See Raw Wikipedia content (toggle)", expanded=False):
    m = page_contents_truncated
    if truncation_message:
        m = truncation_message + "\n\n" + m
    st.write(m)




# data ready from wikipedia, now what to do?


# how many words should the summary be?
max_words = st.slider("Target length in words", min_value=1, max_value=100, value=25)

# 6) show summary from chatgpt
if st.button("Summarize with ChatGPT"):
    if not st.session_state.rate_limiter.allow():
        st.error("Oops, I'm rate limited.  Please wait a bit and try again.   " + st.session_state.rate_limiter.status(verbose=True))
        st.stop()

    with st.spinner("Summarizing…"):
        t0 = time.time()
        prompt = (
            f"Summarize the following Wikipedia article in at most {max_words} words. "
            f"Only output the summary text, no preamble.\n\n"
            f"Title: {page.title}\n\n"
            f"{page_contents_truncated}"
        )
        max_tokens = (max_words + len(prompt)) * 4  # long prompt can hit max_tokens if this is static

        completion = client.chat.completions.create(
            model = model,
            messages=[
                {"role": "system", "content": "You are a scientific and technical summarizer."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens = max_tokens,
        )

        summary = completion.choices[0].message.content.strip()

    st.session_state.summary = summary
    st.session_state.summary_completion = completion
    st.session_state.summary_completion_report = get_est_response_cost(completion, t0)

# 7) haiku
if st.button("Generate Haiku"):
    if not st.session_state.rate_limiter.allow():
        st.error("Oops, I'm rate limited.  Please wait a bit and try again.   " + st.session_state.rate_limiter.status(verbose=True))
        st.stop()
    with st.spinner("generating haiku..."):
        prompt = (
            f"Generate a haiku about the following wikipedia entry: "
            #f"Only output the summary text, no preamble.\n\n"
            f"Title: {page.title}\n\n"
            f"{page_contents_truncated}"
        )
        t0 = time.time()

        max_tokens = (max_words + len(prompt)) * 4  # long prompt can hit max_tokens if this is static

        completion_haiku = client.chat.completions.create(
            model = model,
            messages=[
                {"role": "system", "content": "You are a scientific and technical summarizer and poet."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens = max_tokens,
        )

        haiku = completion_haiku.choices[0].message.content.strip()

    st.session_state.haiku = haiku
    st.session_state.haiku_completion = completion_haiku
    st.session_state.haiku_completion_report = get_est_response_cost(completion_haiku, t0)


# 8) limerick
if st.button("Generate Limerick"):
    if not st.session_state.rate_limiter.allow():
        st.error("Oops, I'm rate limited.  Please wait a bit and try again.   " + st.session_state.rate_limiter.status(verbose=True))
        st.stop()
    with st.spinner("generating limerick..."):
        prompt = (
            f"Generate a limerick about the following wikipedia entry: "
            #f"Only output the summary text, no preamble.\n\n"
            f"Title: {page.title}\n\n"
            f"{page_contents_truncated}"
        )
        t0 = time.time()

        max_tokens = (max_words + len(prompt)) * 4  # long prompt can hit max_tokens if this is static

        completion_limerick = client.chat.completions.create(
            model = model,
            messages=[
                {"role": "system", "content": "You are a scientific and technical summarizer and poet."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens = max_tokens,
        )

        limerick = completion_limerick.choices[0].message.content.strip()

    st.session_state.limerick = limerick
    st.session_state.limerick_completion = completion_limerick
    st.session_state.limerick_completion_report = get_est_response_cost(completion_limerick, t0)

    # st.write(limerick)
    # with st.expander("returned object"):
    #     st.json(completion_limerick.model_dump())


# Display what's been generated

# --- Display summary if we have one ---
if st.session_state.summary is not None:
    st.subheader("Summary")
    st.write(st.session_state.summary)

    #word_count = len(st.session_state.summary.split())
    #st.write(f"I counted {word_count} words in the summary returned by the LLM")

    if st.session_state.summary_completion_report is not None:
        #print("267", st.session_state.summary_completion_report)
        st.text(st.session_state.summary_completion_report)

    if st.session_state.summary_completion is not None:
        with st.expander("Summary – raw completion object"):
            st.json(st.session_state.summary_completion.model_dump())

# --- Display haiku if we have one ---
if st.session_state.haiku is not None:
    st.subheader("Haiku")
    st.write(st.session_state.haiku)

    if st.session_state.haiku_completion_report is not None:
        st.text(st.session_state.haiku_completion_report)

    if st.session_state.haiku_completion is not None:
        with st.expander("Haiku – raw completion object"):
            st.json(st.session_state.haiku_completion.model_dump())

# --- Display limerick if we have one ---
if st.session_state.limerick is not None:
    st.subheader("Limerick")
    st.write(st.session_state.limerick)

    if st.session_state.limerick_completion_report is not None:
        st.text(st.session_state.limerick_completion_report)

    if st.session_state.limerick_completion is not None:
        with st.expander("Limerick – raw completion object"):
            st.json(st.session_state.limerick_completion.model_dump())


st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/006_ai-wikipedia.py)")



