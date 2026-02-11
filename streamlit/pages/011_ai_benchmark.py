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
#from chatting import chat_with_gpt, chat_with_anthropic, chat_with_llm

# -------------------------
# constants
# -------------------------

WORD_MAX_J1_DEFAULT = 30
WORD_MAX_A_DEFAULT = 10
WORD_MAX_B_DEFAULT = 25
WORD_MAX_J8_DEFAULT = 100


PROMPT = """
You must solve the problem carefully.

IMPORTANT:
- The first character in your response must be the letter that is your answer.
- If you can, you should add a probability percentage representing your confidence in your answer
- Example Reply: "A 80%" means "I choose answer A and I'm 80% confident in that reply"
- Example Reply: "E 100%" means "I choose answer E and I'm 100% confident in that reply"
- You may, but are not required, to provide a brief explanation as to how and why you chose your response.  This should be on a new line.

Problem:
{PUZZLE_TEXT}

"""



# -------------------------
# Session state init
# -------------------------

# if "party_A" not in st.session_state:
#     st.session_state.party_A = {}

# if "party_B" not in st.session_state:
#     st.session_state.party_B = {}

# if "party_J" not in st.session_state:
#     st.session_state.party_J = {}
# are these used?
if "parties_defined" not in st.session_state:
    st.session_state.parties_defined = False

if "argument_result" not in st.session_state:
    st.session_state.argument_result = False

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []



if "party_A_word_max" not in st.session_state:
    st.session_state.party_A_word_max = WORD_MAX_A_DEFAULT
if "party_B_word_max" not in st.session_state:
    st.session_state.party_B_word_max = WORD_MAX_B_DEFAULT
if "party_J1_word_max" not in st.session_state:
    st.session_state.party_J1_word_max = WORD_MAX_J1_DEFAULT
if "party_J8_word_max" not in st.session_state:
    st.session_state.party_J8_word_max = WORD_MAX_J8_DEFAULT


# chatgpt suggests I define these in a fucntion so I'm sure they'll get created AFTER any updates to st.session_state vars...

PROP_EXAMPLES = [
            "P equals NP",
            "murder is always wrong",
            "the good of the many outweighs the good of the few",
            "democracy is always the best form of government",
            "there is no solution to the trolley problem",
            "Javier is the true hero of Les Miserable",
            ".jpg should be pronuced JAY-feg",
            "time travel is impossible",
]


def make_prompts():
    return {

        "PROMPT_BASELINE" : f'''
            You are one of three participants in a polite and principled argument.  The participants are:
            1) A - who will argue in favor of the proposition
            2) B - who will argue against the proposition
            3) J - a judge who decides who made the best argument and why. J should consider how well A and B respond to each other's statements.

            The argument is structured as follows:
            1) The rules are shared with all parties.
            2) The proposition is shared with everyone
            3) A, B, and J are assigned their roles
            4) J shares, in {st.session_state.party_J1_word_max} words or less, how they will decide on the winner of the argument.  This should include how well A and B respond to each other's statements.  Let's call this the argument guidelines.
            5) A makes the first statement, {st.session_state.party_A_word_max} words or less, in favor of the proposition.
            6) B makes the next statement, {st.session_state.party_B_word_max} words or less, against the proposition.
            7) Steps 5 and 6 repeat two more times, for a total of six statements.
            8) J decides who won the argument and explains, in {st.session_state.party_J8_word_max} words or less, who won and the reasoning behind the decision.
        ''',

        "PROMPT_A" : "You are participant A, and will argue in favor of the proposition.",
        "PROMPT_B" : "You are participant B, and will argue against the proposition",
        "PROMPT_J" : ("You are the judge J. You will first share the argument guidelines, and after all statements you will decide the winner and explain your reasoning."),


        "PROMPT_J_TURN_1" : (f"Follow step 4: Share the argument guidelines in {st.session_state.party_J1_word_max} words or less.  "
                           f"Do NOT argue yet, just describe how you will judge."),

        "PROMPT_J_TURN_8" : (f"Follow step 8: In {st.session_state.party_J8_word_max} words or less, decide who won the argument  "
                           f"(A or B) and explain your reasoning. Be concise."),


        "PROMPT_A_GO" : (f"Make your statement in favor of the proposition, "
                       f"in {st.session_state.party_A_word_max} words or less. Respond to what has been said so far."),

        "PROMPT_B_GO" : (f"Make your statement against the proposition, "
                       f"in {st.session_state.party_B_word_max} words or less. Respond to what has been said so far."),
    }

# PLAYERS = ["A", "B", "J"]

MODEL_LIST = [
        "gpt-4o-mini",            # .15
        "gpt-5-mini",             # .25 input
        "gpt-5-nano",             # .05 input
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20251001",
]

MAX_TOKENS = 1000
DEFAULT_MODEL_INDEX = 4

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
# Main UI
# -------------------------
st.title("AI Argue")
st.markdown("Let's start an argument." "(inspired by [Argument - Monty Python](https://www.youtube.com/watch?v=ohDB5gbtaEQ)")



st.markdown("Pick a proposition:")
proposition= st.radio("Select a proposition:", PROP_EXAMPLES)

st.markdown("Pick LLMs and word limits for each party")


col1, col2 = st.columns(2)
with col1:
    party_A_model = st.selectbox("Select Party A model:", MODEL_LIST, index = 4)
    party_B_model = st.selectbox("Select Party B model:", MODEL_LIST, index = 4)
    party_J_model = st.selectbox("Select Party J model:", MODEL_LIST, index = 4)

with col2:
    party_A_word_max = st.number_input("Max words A can use per statement", min_value = 5, max_value = 40, key = "party_A_word_max", step = 5)
    party_B_word_max = st.number_input("Max words B can use per statement", min_value = 5, max_value = 40, key = "party_B_word_max", step = 5)
    party_J1_word_max = st.number_input("Max words J can use for guidelines", min_value = 5, max_value = 40, key = "party_J1_word_max", step = 5)
    party_J8_word_max = st.number_input("Max words J can use for final ruling", min_value = 5, max_value = 120, key = "party_J8_word_max", step = 5)


st.divider()






def call_llm(party_model, role_prompt, turn_prompt, conversation_history = []):

    conversation_so_far = "\n".join(conversation_history)

    full_user_prompt = (
        f"{role_prompt}\n\n"
        f"Proposition: {st.session_state.proposition}\n\n"
        f"Conversation so far:\n{conversation_so_far}\n\n"
        f"{turn_prompt}\n\n"
    )


    if party_model.startswith("gpt"):
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=party_model,
            messages=[
                {"role": "system", "content": prompts["PROMPT_BASELINE"]},
                {"role": "user", "content": full_user_prompt},
            ],
            max_tokens=MAX_TOKENS,
        )
        #print(f"call_llm returning {resp.choices[0].message.content.strip()}")
        message = response.choices[0].message.content.strip()
        return message


    if party_model.startswith("claude"):
            if not ANTHROPIC_API_KEY:
                raise RuntimeError("ANTHROPIC_API_KEY is not set.")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=party_model,
                max_tokens=MAX_TOKENS,
                system=prompts["PROMPT_BASELINE"],
                messages=[
                    {"role": "user", "content": full_user_prompt},
                ],
            )

            # Anthropic returns a list of content blocks - sometimes? 
            message = response.content[0].text
            return message
    print(f"error - unk model {party_model}")
    raise ValueError(f"Unknown model name: {party_model}")
# ------




# -------------------------
# Start argument button
# -------------------------
if st.button("Start the argument 🥊"):
    # Rate limit check
    if not st.session_state.rate_limiter.allow():
        st.error(
            "Oops, you're rate limited. "
            + st.session_state.rate_limiter.status(verbose=True)
        )
        st.stop()

    prompts = make_prompts()



    st.session_state.party_A = {"model": party_A_model}
    st.session_state.party_B = {"model": party_B_model}
    st.session_state.party_J = {"model": party_J_model}
    st.session_state.parties_defined = True
    st.session_state.proposition = proposition

    # reset history/result
    st.session_state.conversation_history = []
    st.session_state.argument_result = None

    output_area = st.container()

    conversation_history = st.session_state.conversation_history


    print("let's rumble!")


    # --- Step 4: J gives argument guidelines ---
    with output_area:
        with st.spinner("J (judge) is thinking about the guidelines..."):
            guidelines = call_llm(
                party_J_model,
                prompts["PROMPT_J"],
                prompts["PROMPT_J_TURN_1"],
                conversation_history,
            )
        st.markdown("**J (guidelines):** " + guidelines)
    conversation_history.append(f"J: {guidelines}")

    st.divider()

    # --- Steps 5–7: 3 rounds of A / B ---
    for arg_round in range(1, 4):
        with output_area:
            st.markdown(f"### Round {arg_round}")

        with output_area:
            with st.spinner(f"Round {arg_round}: A is thinking..."):
                arg_A_response = call_llm(
                    party_A_model,
                    prompts["PROMPT_A"],
                    prompts["PROMPT_A_GO"],
                    conversation_history,
                )
            st.markdown(f"**A (round {arg_round}):** {arg_A_response}")
        conversation_history.append(f"A (round {arg_round}): {arg_A_response}")

        with output_area:
            with st.spinner(f"Round {arg_round}: B is thinking..."):
                arg_B_response = call_llm(
                    party_B_model,
                    prompts["PROMPT_B"],
                    prompts["PROMPT_B_GO"],
                    conversation_history,
                )
            st.markdown(f"**B (round {arg_round}):** {arg_B_response}")
        conversation_history.append(f"B (round {arg_round}): {arg_B_response}")
    
        with output_area:
            st.divider()

    # --- Step 8: J decides ---
    with output_area:
        with st.spinner("J is deciding..."):
            results = call_llm(
                party_J_model,
                prompts["PROMPT_J"],
                prompts["PROMPT_J_TURN_8"],
                conversation_history,
            )
        st.markdown("### Judge J's decision")
        st.write(results)

    conversation_history.append(f"J (decision): {results}")
    st.session_state.argument_result = results

    st.session_state.conversation_history = conversation_history



st.divider()
with st.expander("Full argument transcript", expanded=False):
    if st.session_state.conversation_history:
        for line in st.session_state.conversation_history:
            st.markdown(line)
    else:
        st.caption("No argument yet — press the button above to start.")




st.write("Script ran at", datetime.datetime.now())

# -------------------------
# 4) GitHub link directly under the input
# -------------------------
st.markdown(
    "[code_on_github](https://github.com/databloomnet/databloom_codes/blob/main/streamlit/pages/011_ai_benchmark.py)"
)

