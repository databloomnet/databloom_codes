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
st.title("🌱 apps.databloom.net")

#st.markdown("# Welcome to apps.databloom.net codes!")
st.markdown('#### © 2025 Jeremy Bloom')
#st.subheader("Jeremy Bloom")


verify_session()


msg_intro = r"""I put together this apps.databloom.net microsite to share some of the Python, AI, analytics, and cloud projects I’ve been working on.

Most visitors are here for one of two reasons:
1) Friends and colleagues interested in seeing some of the things I build and talk about
2) Prospective employers or collaborators exploring a full-time and/or contract fit

For the *first group*, I take requests and often add examples here that I want
to demo, explain, or share more widely. Yes, I’m a full-fledged nerd, and I love this stuff.

For the *second group*, most of what you’ll see are coding examples around GenAI and related topics. 
While I enjoy coding (and still do plenty of it), I don’t think of myself primarily as a heads-down developer. 
I’m most interested in long-term Product (Management | Strategy | Owner) roles. 
For a broader view of my background and interests, check out [databloom.net](https://www.databloom.net).  One other note: I've never been too interested in front-end implementation.  I know enough about to get by, 
but you may find the presentation it a little bare bones.

Regardless of why you’re here, you’re welcome to contact me at firstname @ bloomfamily.com or firstname @ this domain (which forwards to the former). 
You can also find me on [LinkedIn](https://www.linkedin.com/in/jeremybloom/).
"""

with st.expander("What is apps.databloom.net?", expanded=False):
    st.markdown(msg_intro)




msg_contents = r"""
Some example apps are on the left.  Or you can click on stuff below...
- TEMP: for right now  just use the menu on the left to find what's active
- [streamlit reminders](streamlit_reminders) - a reference page I built for getting up to speed on streamlit. 
- [logger](logger) - simple logging app
- [echoer](echoer) - toy streamlit app to test reading and writing
- [timer](timer) - stopwatch
- [ai1](ai01) - hello, chat gpt
- chatter – simple chatting with LLMs
- RAG Lite – doc Q&A prototype
"""
with st.expander("What can I do here?", expanded=True):
    st.markdown(msg_contents)

msg_aboutTheSite = r"""
This site is written in python with streamlit, and hosted on an aws ec2 server.  The larger site is running on an aws s3 bucket with cloudfront.  nginx and certbot are also doing their thing.

All of databloom.net is on [github](https://github.com/databloomnet).  For my fellow learners, I try to link each page like [this](https://github.com/databloomnet/databloom_codes/blob/main/bloomcode.py) so you can see the source.
"""
with st.expander("What is apps.databloom.net running on?", expanded=False):
    st.markdown(msg_aboutTheSite)



st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/bloomcode.py)")

