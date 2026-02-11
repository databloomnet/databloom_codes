# ai-argue.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os

from rate_limiter import RateLimiter
from openai import OpenAI
import anthropic
from response_parser import get_response_summary
from chatting import chat_with_llm #, chat_with_gpt, chat_with_anthropic


from bs4 import BeautifulSoup
import re
import requests
from textwrap import dedent


# -------------------------
# constants
# -------------------------
MODEL_LIST = [
        #"gpt-4o-mini",            # .15
        "gpt-5-mini",             # .25 input
        "gpt-5-nano",             # .05 input
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
]

MAX_TOKENS = 2000
DEFAULT_MODEL_INDEX = 2

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
# if "conversation" not in st.session_state:
#     # Each item: {"role": "user"|"assistant", "content": str}
#     st.session_state.conversation = []

MODE_AWAIT_INFO = "enter_initial_info"
MODE_REVISE = "enter_revision"


if "mode" not in st.session_state:
    print("NO MODE, SO SETTING TO AWAIT INFO")
    st.session_state.mode = MODE_AWAIT_INFO


if "model" not in st.session_state:
    st.session_state.model = MODEL_LIST[DEFAULT_MODEL_INDEX]
if "model_index" not in st.session_state:
    st.session_state.model_index = DEFAULT_MODEL_INDEX


if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "bio" not in st.session_state:
    st.session_state.bio = ""

# -------------------------
# Sidebar: model selection & reset
# -------------------------
with st.sidebar:
    st.header("Chat settings")
    model_locked = True

    if st.session_state.mode == MODE_AWAIT_INFO:
        st.markdown("Once you hit generate the LLM choice is locked.")
        model_locked = False
    elif st.session_state.mode == MODE_REVISE:
        st.markdown("In order to change LLM you need to reset the page.")
        model_locked = True
    else:
        st.error("unrecog mode")

    model = st.selectbox("Choose model:", 
        options = MODEL_LIST,
        index = st.session_state.model_index,
        disabled = model_locked, # = st.session_state.locked
        help = "select a model to converse with",
    )
    # print("model:", model)
    st.session_state.model = model
    st.session_state.model_index = MODEL_LIST.index(model)

    if model_locked:
        if st.button("Reset"):
            model_locked = False
            st.session_state.mode = MODE_AWAIT_INFO
            st.session_state.prompt = ""
            st.session_state.bio = ""

            # reset all TODO
            # st.session_state.prompt = ""
            # st.session_state.output= ""
            # st.session_state.revisions = ""
            # st.session_state.locked = False
            #st.session_state.change_history = ""
            st.rerun()           




# page setup
st.title("AI Intro Generator")
st.markdown("Generate introduction text by entering some info and related web sites.")


def fetch_website_content(url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; BioGenerator/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Limit length
        return text[:3000]
    except Exception as e:
        return f"[Could not fetch content: {str(e)}]"

def build_prompt_initial_bio(name: str, about: str, websites: dict) -> str:
    """
    build prompt to get first draft of bio 
    """
    website_context = ""
    if len(websites) > 0:
        for url in websites:
            content = fetch_website_content(url)
            website_context += f"\n\n--- Content from {url} ---\n{content}"

    prompt = dedent(f"""
        Generate a professional website bio for the person named below.  It should be 2-3 paragraphs long.

        Name: {name}

        Bio Information provided:
        {about}

        Related website content for context (if any):
        {website_context}

        Based on this information, write a compelling, professional bio (2-3 paragraphs) 
        suitable for a personal or professional website. The bio should:
        - Be written in third person
        - Highlight key accomplishments and expertise
        - Sound natural and engaging
        - Incorporate relevant details from the website content where appropriate

        Return only the bio text, no additional commentary.
    """).strip()
    return prompt

def build_prompt_bio_changes(latest_bio: str, bio_changes: str) -> str:
    if latest_bio == "":
        st.error("no latest_bio provided")
        return
    if bio_changes == "":
        st.error("no bio_changes requested")
        return 


    prompt = dedent(f"""
        Create a new website bio based on an existing one.  Please review the LATEST_BIO and the following CHANGES_REQUESTED and modify the bio text.
        LATEST_BIO:
        {latest_bio}
        CHANGES_REQUESTED:
        {bio_changes}
        
        Return only the bio text, no additional commentary.
    """).strip()
    return prompt



        
        







# -------------------------
# Main UI
# -------------------------



# if prompt_locked is False, show the prompt form
if st.session_state.mode == MODE_AWAIT_INFO:
    """
    MODE_AWAIT_INFO
    - get info from user
    - generate a prompt
    - call and get response
    - rerun
    """
    st.subheader("Enter some info about you")

    with st.form("profile_form"):
        """
        fills in: name, about, websites
        """
        name = st.text_input("Full Name", placeholder="John Smith")
        st.markdown("enter some info about you such as: I'm a Production Sound Mixer.  I do sound for movies, shorts, and commercials.  I'm based in San Jose California and cover the entire San Francisco Bay Area.  I'm early in my career, and open to pro bono jobs with students.")
        about = st.text_area(
            "Things about me...", 
            placeholder="Current role, background, goals,  expertise, achievements, interests, etc.\n\nExample: I'm a Production Sound Mixer...",
            height=250
        )

        st.markdown("Optionally, add one or more URLs that are about you such as: https://www.imdb.com/name/nm13455867/ and https://www.backstage.com/u/rylee-blechman/.")

        websites = []
        for i in range(3):
            url = st.text_input(f"Website {i+1}", key=f"url_{i}", placeholder="https://www.imdb.com/name/nm13455867").strip()
            if url:
                websites.append(url)

        submitted = st.form_submit_button("Generate")
        # waits for submitted button to be clicked

        if submitted:
            if not name:
                st.error("Please enter a name")
            if not about:
                st.error("Please enter some info about you")
            
            # at this point, we have the inputs and can generate the prompt
            st.session_state.prompt = build_prompt_initial_bio(name, about, websites)
            
            if st.session_state.prompt:
                st.write("Prompt created as:")
                st.info(st.session_state.prompt)

                st.session_state.bio, junk = chat_with_llm(st.session_state.model, st.session_state.prompt, "")
                #print("280: chat_with_llm returned:", st.session_state.bio)
                st.session_state.mode = MODE_REVISE
                st.rerun()

#print("282: st.session_state.mode:", st.session_state.mode)

if st.session_state.mode == MODE_REVISE:
    #print("285: st.session_state.mode:", st.session_state.mode)
    st.write(f"Bio by {st.session_state.model}:")
    st.markdown(st.session_state.bio)

    with st.expander("To see prompt data, click to unfold", expanded=False):
        st.code(st.session_state.prompt)

    st.subheader("Revisions")
    with st.form("Enter any requested revisions below..."):
        changes_requested = st.text_area(
            "Any updated instructions?",
            placeholder="mention how smart I am..."
        )
        changes = st.form_submit_button("Apply Changes")

        if changes:
            #st.session_state.revisions = changes_requested
            st.session_state.prompt = build_prompt_bio_changes(st.session_state.bio, changes_requested)
            st.session_state.bio, junk = chat_with_llm(st.session_state.model, st.session_state.prompt, "")
            print("304: chat_with_llm returned:", st.session_state.bio)


            st.rerun()   

st.write("Script ran at", datetime.datetime.now())

# -------------------------
# 4) GitHub link directly under the input
# -------------------------
st.markdown(
    "[code_on_github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/012_ai_biogen.py)"
)

