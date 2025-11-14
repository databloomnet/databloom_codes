# databloomnet_codes
"""
Jeremy Bloom main databloom net demo pages

(.venv) poe:databloom.net % streamlit run databloomnet-examples.py  --server.address 0.0.0.0 --server.port 8501
"""

import streamlit as st
from datetime import datetime
import uuid
from logger import write_log, read_log, verify_session




st.set_page_config(page_title="databloom.net", page_icon="🌱")
st.title("🌱 databloom.net")

st.header("Welcome to databloom.net codes!")

msg=r"""I, Jeremy Bloom, put together this (Streamlit) app to share some of the things python/AI/analytics/cloud stuff I've learned over my career.

I anticipate most visiters will be here for one of two reasons:
1) Friends and colleagues interesting in seeing some of the stuff I write and talk about
2) Prospective employers interested in engaging on a full time and/or contractual basis.

For the first group, I take requests, 
and often add examples here that I want to speak to or share more widely.

For the second group, this page is about my python skills.
While I enjoy coding, I'm especially
interested in long-term Product (Management|Strategy|Owner)
type roles.  See 
the main web site for my broader background.  

You're invited to contact me at firstname @ this domain or @ bloomfamily.com

"""



st.markdown(msg)


st.write("Pick something from the sidebar (left).")
st.markdown("""
- streamlit - getting up to speed on streamlit
    - streamlit reminders - a reference page I built for getting up to speed on streamlit
    - echoer - toy streamlit app
    - logger - example logger app
    - timer - stopwatch
- 
- example...
- **Agent Chat** – tool-using agent with planning
- **RAG Lite** – doc Q&A prototype
- **Workflow Runner** – multi-step planner
""")

verify_session()

# pages = {
#     "Your account": [
#         st.Page("pages/001_streamlit_reminders.py", title="bob"),
#         st.Page("pages/002_logger.py", title="ed"),
#     ],
#     "Resources": [
#         st.Page("pages/003_echoer.py", title="ed"),
#         st.Page("pages/004_timer.py", title="ed"),
#     ],
# }

# pg = st.navigation(pages)
# #pg = st.navigation(pages,position="top")
# pg.run()

# with st.sidebar:
#     st.title("Navigation")

#     # Create an expander for "Page 1"
#     with st.expander("Page 1 Options"):
#         st.sidebar.page_link("003_timer.py", label="Home")

#         st.write("Content related to Page 1.")
#         st.button("Action for Page 1")

#     # Create another expander for "Page 2"
#     with st.expander("Page 2 Options"):
#         st.write("Content related to Page 2.")
#         st.checkbox("Enable Feature X")

# streamlit run streamlit_app.py --server.port 8501
# (.venv) poe:databloom.net % 
# streamlit run jdb_streamlit_main.py --server.address 0.0.0.0 --server.port 8501


