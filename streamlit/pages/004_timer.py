import streamlit as st
import datetime
import time


st.title("Clock")

if "event_clock_time" not in st.session_state:
    st.session_state.event_clock_time = []
if "event_epoch_time" not in st.session_state:
    st.session_state.event_epoch_time = []

col1, col2 = st.columns(2)


if col1.button("🔄 Reset", type="secondary"):
    st.session_state.event_clock_time = []
    st.session_state.event_epoch_time = []
    st.rerun()

#if not st.session_state.event_clock_time:
if len(st.session_state.event_clock_time) == 0:
    label = "Click Me"
    if col2.button(label, type='primary', key=f"btn_{len(st.session_state.event_clock_time)}"):
        clock_time = datetime.datetime.now()
        epoch_time = time.time()
        st.session_state.event_clock_time.append( clock_time )
        st.session_state.event_epoch_time.append( epoch_time )
        st.rerun()  # ensures immediate re-render so the new success shows above this new button

else:
    label = "Click again"    
    if col2.button(label, type='primary', key=f"btn_{len(st.session_state.event_clock_time)}"):
        clock_time = datetime.datetime.now()
        epoch_time = time.time()
        st.session_state.event_clock_time.append( clock_time )
        st.session_state.event_epoch_time.append( epoch_time )
        st.rerun()  # ensures immediate re-render so the new success shows above this new button


# render all events
num_clicks = len(st.session_state.event_clock_time)
msg = ""
for i in range(num_clicks):
    #st.write(f"i is **{i}**")
    clock_time = st.session_state.event_clock_time[i]
    epoch_time = st.session_state.event_epoch_time[i]
    msg += f"Click {i + 1} was at {clock_time:%Y-%m-%d %H:%M:%S}"

    if i == 0:
        msg += "\n"
        pass
        #msg += f"Click {i + 1} was at {clock_time:%Y-%m-%d %H:%M:%S}."
        #st.success(f"Click {i + 1} was at {clock_time:%Y-%m-%d %H:%M:%S}.")
    else:
        last_epoch_time = st.session_state.event_epoch_time[i - 1]

        delta = epoch_time - last_epoch_time

        # st.success(
        #     f"Click {i + 1} was at {clock_time:%Y-%m-%d %H:%M:%S}."
        #     f"  Seconds elapsed since this and last click: {delta:0.3f}s."
        # )

        msg += "  ( {:2.3f}s between clicks)\n".format( epoch_time - last_epoch_time )
if num_clicks:
    #st.success(msg)
    st.text(msg)



st.write("[code](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/004_timer.py)")

