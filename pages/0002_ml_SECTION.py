# streamlit
"""
example streamlit functions
uses logger.py
"""
import streamlit as st
from datetime import datetime
from logger import read_log, read_log, clear_log, verify_session, prompt_for_log, get_log_total_size, get_log_total_lines



st.title("Logger")
verify_session()
st.header("Streamlit Examples")


# Initialize log in session state
if "log" not in st.session_state:
    st.session_state.log = []


st.page_link("pages/003_echoer.py")

#st.markdown("[Go to echoer](pages/003_echoer.py)")

#st.markdown("[Go to echoer](003_echoer.py)")

#st.markdown("[Go to echoer](003_echoer.py)")





