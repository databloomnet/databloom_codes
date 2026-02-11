# databloomnet_codes
"""
Jeremy Bloom
app.databloom.net
"""

import streamlit as st
from datetime import datetime
import uuid
from logger import write_log, read_log, verify_session

from rate_limiter import RateLimiter


rate_limiter_max_requests = 15
rate_limiter_inteval_seconds = 300 # 5 minutes

if  "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(max_requests=rate_limiter_max_requests, interval_sec= rate_limiter_inteval_seconds )




st.set_page_config(page_title="databloom.net", page_icon="🌱")

verify_session()

# --- Page declarations ---
home = st.Page("pages/home.py", title="Home", icon="🌱", default=True)

ai_pages = [
    st.Page("pages/005_ai-hello.py", title="AI Hello", icon="👋", url_path="ai-hello"),
    st.Page("pages/006_ai-wikipedia.py", title="AI Wikipedia", icon="📚", url_path="ai-wikipedia"),
    st.Page("pages/007_ai-playground.py", title="AI Playground", icon="🎮", url_path="ai-playground"),
    st.Page("pages/008_ai-ask.py", title="AI Ask", icon="💬", url_path="ai-ask"),
    st.Page("pages/009_ai-converse.py", title="AI Converse", icon="🗣️", url_path="ai-converse"),
    st.Page("pages/010_ai-argue.py", title="AI Argue", icon="🥊", url_path="ai-argue"),
    st.Page("pages/011_ai_benchmark.py", title="AI Benchmark", icon="📊", url_path="ai_benchmark"),
    st.Page("pages/012_ai_biogen.py", title="AI Intro Generator", icon="📝", url_path="ai_biogen"),
]

tool_pages = [
    st.Page("pages/001_streamlit_reminders.py", title="Streamlit Reminders", icon="📌", url_path="streamlit_reminders"),
    st.Page("pages/002_logger.py", title="Logger", icon="📋", url_path="logger"),
    st.Page("pages/003_echoer.py", title="Echoer", icon="🔊", url_path="echoer"),
    st.Page("pages/004_timer.py", title="Timer", icon="⏱️", url_path="timer"),
]

pg = st.navigation({
    "": [home],
    "AI Apps": ai_pages,
    "Tools": tool_pages,
})
pg.run()
