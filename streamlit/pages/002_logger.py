# logs.py
"""
example streamlit function
uses logger.py
"""
import streamlit as st
from datetime import datetime
from logger import read_log, read_log, clear_log, verify_session, prompt_for_log, get_log_total_size, get_log_total_lines



st.title("Logger")
verify_session()

# Initialize log in session state
if "log" not in st.session_state:
    st.session_state.log = []

st.markdown("Some simple logging tools.  No AI stuff here...- Jeremy")

tab1, tab2, tab3 = st.tabs(["View Log", "Write to Log", "Clear Log"])

with tab1:
    #st.subheader("viewing...")
    col1, col2, col3, col4, col5 = st.columns(5)

    btn_last_10 = col1.button("Last 10 Entries")
    btn_last_100 = col2.button("Last 100 Entries")
    btn_all = col3.button("All Entries")
    num_entries = col4.text_input("num entries", max_chars=5, width=100)
    btn_last_x = col4.button(f"Last {num_entries}")
    btn_info = col5.button("Log Info")

    #st.write(f"{num_entries}")
    #st.write(f"{type(num_entries)}")

    #if col1.button("Last 10"):
    if btn_last_10:
        st.subheader("Last 10 Entries")
        st.text(read_log(10))

    #elif col2.button("Last 100"):
    if btn_last_100:
        st.subheader("Last 100 Entries")
        st.text(read_log(100))

    #elif col3.button("All"):
    if btn_all:
        st.subheader("All Entries")
        st.text(read_log())

    if btn_last_x:
        st.subheader("Last X Entries")
        st.text(read_log(int(num_entries)))


    #elif col4.button("Info"):
    if btn_info:
        st.subheader("Log Info")
        # get info
        m = "{:d} messages totalling {:s}".format(get_log_total_lines(), get_log_total_size())
        st.text(m)


with tab2:
    #st.subheader("writing...")
    prompt_for_log()

with tab3:
    #st.subheader("wiping...")
    m = "{:d} messages totalling {:s}".format(get_log_total_lines(), get_log_total_size())        
    st.subheader(f"Log has {m}")
    st.info(f"Log has {m}")
    col1, col2 = st.columns(2)
    if col2.button("Keep last 100 lines"):
        clear_log(keep_last=100)
        m = "{:d} messages totalling {:s}".format(get_log_total_lines(), get_log_total_size())        
        st.info(f"Log now has {m}")

    if col1.button("Clear all logs"):
        clear_log()
        st.warning("All logs cleared!")




st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/002_logger.py)")
st.write("[code lib](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/logger.py)")

