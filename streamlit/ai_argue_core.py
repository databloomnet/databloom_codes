# ai_argue_core.py
#
# The AI Argue debate engine: prompts, LLM calls, winner parsing.
# No streamlit import here; it is used by pages/010_ai-argue.py and scripts/run_batch.py.

import contextlib
import datetime
import hashlib
import os
import re
import time

import anthropic
from openai import OpenAI

MAX_TOKENS = 1000

# -------------------------
# Prompts
# -------------------------
# Templates are filled with the word limits by make_prompts().
# judge_prompt_hash is computed from the unfilled templates.

PROMPT_TEMPLATES = {

    "PROMPT_BASELINE" : '''
            You are one of three participants in a polite and principled argument.  The participants are:
            1) A - who will argue in favor of the proposition
            2) B - who will argue against the proposition
            3) J - a judge who decides who made the best argument and why. J should consider how well A and B respond to each other's statements.

            The argument is structured as follows:
            1) The rules are shared with all parties.
            2) The proposition is shared with everyone
            3) A, B, and J are assigned their roles
            4) J shares, in {words_j1} words or less, how they will decide on the winner of the argument.  This should include how well A and B respond to each other's statements.  Let's call this the argument guidelines.
            5) A makes the first statement, {words_a} words or less, in favor of the proposition.
            6) B makes the next statement, {words_b} words or less, against the proposition.
            7) Steps 5 and 6 repeat two more times, for a total of six statements.
            8) J decides who won the argument and explains, in {words_j8} words or less, who won and the reasoning behind the decision.
        ''',

    "PROMPT_A" : "You are participant A, and will argue in favor of the proposition.",
    "PROMPT_B" : "You are participant B, and will argue against the proposition",
    "PROMPT_J" : ("You are the judge J. You will first share the argument guidelines, and after all statements you will decide the winner and explain your reasoning."),


    "PROMPT_J_TURN_1" : ("Follow step 4: Share the argument guidelines in {words_j1} words or less.  "
                         "Do NOT argue yet, just describe how you will judge."),

    "PROMPT_J_TURN_8" : ("Follow step 8: In {words_j8} words or less, decide who won the argument  "
                         "(A or B) and explain your reasoning. Be concise. "
                         'End your response with a final line exactly "WINNER: A" or "WINNER: B".'),


    "PROMPT_A_GO" : ("Make your statement in favor of the proposition, "
                     "in {words_a} words or less. Respond to what has been said so far."),

    "PROMPT_B_GO" : ("Make your statement against the proposition, "
                     "in {words_b} words or less. Respond to what has been said so far."),
}


def make_prompts(words_a, words_b, words_j1, words_j8):
    limits = {"words_a": words_a, "words_b": words_b, "words_j1": words_j1, "words_j8": words_j8}
    return {name: template.format(**limits) for name, template in PROMPT_TEMPLATES.items()}


def judge_prompt_hash():
    """sha256 of the judge's system prompt plus both judge turn templates, before word limits are filled in."""
    text = "\n".join([
        PROMPT_TEMPLATES["PROMPT_BASELINE"],
        PROMPT_TEMPLATES["PROMPT_J_TURN_1"],
        PROMPT_TEMPLATES["PROMPT_J_TURN_8"],
    ])
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_winner(ruling_text):
    """Return "A" or "B" from a final line "WINNER: A" / "WINNER: B", else "unparsed"."""
    lines = [line.strip() for line in (ruling_text or "").splitlines() if line.strip()]
    if not lines:
        return "unparsed"
    last = lines[-1].strip("*_`. ").upper()
    m = re.fullmatch(r"WINNER:\s*\**\s*([AB])", last)
    return m.group(1) if m else "unparsed"


# -------------------------
# LLM calls
# -------------------------

def call_llm(party_model, system_prompt, role_prompt, turn_prompt, proposition, conversation_history):
    """One LLM call. Returns (text, tokens_in, tokens_out)."""

    conversation_so_far = "\n".join(conversation_history)

    full_user_prompt = (
        f"{role_prompt}\n\n"
        f"Proposition: {proposition}\n\n"
        f"Conversation so far:\n{conversation_so_far}\n\n"
        f"{turn_prompt}\n\n"
    )

    if party_model.startswith("gpt"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        client = OpenAI(api_key=api_key)
        # gpt-5 models are reasoning models: they reject max_tokens and temperature,
        # and hidden reasoning tokens count against max_completion_tokens
        extra_args = {"reasoning_effort": "minimal"} if party_model.startswith("gpt-5") else {}
        response = client.chat.completions.create(
            model=party_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_user_prompt},
            ],
            max_completion_tokens=MAX_TOKENS,
            **extra_args,
        )
        message = (response.choices[0].message.content or "").strip()
        usage = response.usage
        return message, usage.prompt_tokens, usage.completion_tokens

    if party_model.startswith("claude"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=party_model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": full_user_prompt},
            ],
        )
        message = "".join(block.text for block in response.content if block.type == "text").strip()
        return message, response.usage.input_tokens, response.usage.output_tokens

    raise ValueError(f"Unknown model name: {party_model}")


class DebateCallError(Exception):
    pass


def _call_with_retry(*args):
    """Retry once on API error."""
    try:
        return call_llm(*args)
    except Exception as first_error:
        print(f"ai_argue_core: call failed, retrying once: {first_error!r}")
        time.sleep(2)
        try:
            return call_llm(*args)
        except Exception as second_error:
            raise DebateCallError(repr(second_error)) from second_error


# -------------------------
# Debate
# -------------------------

def run_debate(proposition, model_a, model_b, model_j, words_a, words_b, words_j1, words_j8, rounds=3,
               turn_context=None, on_statement=None):
    """Run one full debate and return a dict with the guidelines, statements, ruling, winner and token usage.

    Optional UI hooks (the page uses these; the batch script doesn't):
      turn_context(step, round_num) -> context manager wrapped around each LLM call
      on_statement(step, round_num, text) -> called after each statement
    step is one of "guidelines", "A", "B", "ruling".
    """
    turn_context = turn_context or (lambda step, round_num: contextlib.nullcontext())
    on_statement = on_statement or (lambda step, round_num, text: None)

    prompts = make_prompts(words_a, words_b, words_j1, words_j8)
    system_prompt = prompts["PROMPT_BASELINE"]

    result = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
        "proposition": proposition,
        "model_a": model_a,
        "model_b": model_b,
        "model_j": model_j,
        "words_a": words_a,
        "words_b": words_b,
        "words_j1": words_j1,
        "words_j8": words_j8,
        "rounds": rounds,
        "judge_prompt_hash": judge_prompt_hash(),
        "guidelines": None,
        "statements": [],          # [{"step", "round", "model", "text"}]
        "ruling_text": None,
        "winner": None,
        "usage": [],               # [{"step", "round", "model", "tokens_in", "tokens_out"}]
        "conversation_history": [],
        "status": "ok",
        "error": None,
    }
    history = result["conversation_history"]

    def turn(step, round_num, model, role_prompt, turn_prompt):
        with turn_context(step, round_num):
            text, tokens_in, tokens_out = _call_with_retry(
                model, system_prompt, role_prompt, turn_prompt, proposition, history
            )
        result["usage"].append({"step": step, "round": round_num, "model": model,
                                "tokens_in": tokens_in, "tokens_out": tokens_out})
        result["statements"].append({"step": step, "round": round_num, "model": model, "text": text})
        on_statement(step, round_num, text)
        return text

    try:
        # Step 4: J gives argument guidelines
        guidelines = turn("guidelines", 0, model_j, prompts["PROMPT_J"], prompts["PROMPT_J_TURN_1"])
        result["guidelines"] = guidelines
        history.append(f"J: {guidelines}")

        # Steps 5-7: rounds of A / B
        for arg_round in range(1, rounds + 1):
            arg_a = turn("A", arg_round, model_a, prompts["PROMPT_A"], prompts["PROMPT_A_GO"])
            history.append(f"A (round {arg_round}): {arg_a}")
            arg_b = turn("B", arg_round, model_b, prompts["PROMPT_B"], prompts["PROMPT_B_GO"])
            history.append(f"B (round {arg_round}): {arg_b}")

        # Step 8: J decides
        ruling = turn("ruling", rounds + 1, model_j, prompts["PROMPT_J"], prompts["PROMPT_J_TURN_8"])
        result["ruling_text"] = ruling
        result["winner"] = parse_winner(ruling)
        history.append(f"J (decision): {ruling}")

    except DebateCallError as e:
        result["status"] = "error"
        result["error"] = str(e)

    result["tokens_in"] = sum(u["tokens_in"] for u in result["usage"])
    result["tokens_out"] = sum(u["tokens_out"] for u in result["usage"])
    return result
