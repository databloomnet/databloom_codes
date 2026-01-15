# logger.py
"""
logger functions for streamlit project
"""

import datetime
import os
import streamlit as st
import uuid

LOG_FILE = "app.log"

def verify_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:6]
        write_log("connected")


def write_log(message: str):
    """
    Append a timestamped log entry to the app.log file.

    Args:
        message (str): The message to log.
        user_id (str, optional): Session or user identifier (optional).
    """

    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    # if 1+ folder name(s) is/are in LOG_FILE, create it/them
    # if no folder name, just return "." to makedirs

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "session_id" in st.session_state:
        sid = st.session_state.session_id
    else:
        sid = "?"

    line = f"[{timestamp}][{sid}] {message}\n"


    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def read_log(n: int | None = None) -> str:
    """
    Read log entries from disk.

    Args:
        n (int, optional): If given, return only the last n lines.
    Returns:
        str: The log contents as a string.
    """
    #write_log("read_log")

    if not os.path.exists(LOG_FILE):
        return "No log file found."

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if n is not None:
        lines = lines[-n:]

    return "".join(lines)


def clear_log(keep_last: int | None = None):
    """
    Clear the log file.

    Args:
        keep_last (int, optional): If provided, keeps only the last N lines of the log.
                                   If None, clears the file completely.
    """
    if not os.path.exists(LOG_FILE):
        return

    if keep_last is not None and keep_last > 0:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines_to_keep = lines[-keep_last:]
    else:
        lines_to_keep = []

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines_to_keep)

def prompt_for_log():
    if "log_message_input" not in st.session_state:
        st.session_state.log_message_input = ""

    # Callback runs in a separate step where it's legal to mutate the key
    def _write_and_clear():
        msg = st.session_state.log_message_input.strip()
        if msg:
            write_log(msg)
            st.session_state.log_message_input = ""   # safe here
            st.session_state.log_status = "Message written to log."
        else:
            st.session_state.log_status = "Please enter a message."

    st.text_input("Message:", key="log_message_input")
    st.button("Write to Log", type="primary", on_click=_write_and_clear)

    # show status from callback (and clear it after display)
    if st.session_state.get("log_status"):
        st.success(st.session_state.pop("log_status"))

    # msg = st.text_input("Message:", key="log_message_input")

    # if st.button("Write to Log", type="primary"):
    #     if msg.strip():
    #         write_log(msg)
    #         # st.success("✅ Message written to log.")
    #         # clear text input after success
    #         st.session_state.log_message_input = "" # breaks as can't be modified once instantiated
    #     else:
    #         st.warning("Please enter a message before logging.")

def get_log_total_lines():
    if not os.path.exists(LOG_FILE):
        return "No log file found."

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return len(lines)

def get_log_total_size():
    if not os.path.exists(LOG_FILE):
        return "No log file found."

    size_bytes = os.path.getsize(LOG_FILE)

    # clever - chatgpt... Convert to human-readable units
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024

    return f"{size_bytes:.1f} TB"


