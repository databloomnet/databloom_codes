# response_parser.py
"""
simple response parsing
"""

import datetime
import streamlit as st
from openai import OpenAI


VALID_KEYS_TOP = ["id", "created",  "model", "object"]
VALID_KEYS_CHOICES_0_MESSAGE = ["content", "refusal"]
VALID_KEYS_USAGE = ["completion_tokens", "prompt_tokens", "total_tokens"]
VALID_KEYS_USAGE_COMPLETION_DETAILS = ["reasoning_tokens"]


def get_response_info(completion, list_of_keys):
    # for now assume chatgpt

    #print(type(completion))
    #print(completion)
    #print("argh")

    warnings = []
    response = {}
    #print(response.model_dump())
    #print("list_of_keys:", list_of_keys)
    for req_key in list_of_keys:
        if req_key in VALID_KEYS_TOP:
            response[req_key] = getattr(completion, req_key)
        elif req_key in VALID_KEYS_USAGE:
            response[req_key] = getattr(completion.usage, req_key)
        elif req_key in VALID_KEYS_USAGE_COMPLETION_DETAILS:
            response[req_key] = getattr(completion.usage.completion_tokens_details, req_key) 
        elif req_key in VALID_KEYS_CHOICES_0_MESSAGE:
            response[req_key] = getattr(completion.choices[0].message, req_key) 
        else:
             warnings.append(f"no handling for {req_key}")

    if len(warnings):
        print(warnings)
    
    return response

def get_est_response_cost(response, t0 = 0):

    pt = response.usage.prompt_tokens
    ct = response.usage.completion_tokens
    tt = response.usage.total_tokens
    re = response.usage.completion_tokens_details.reasoning_tokens
    calc_output = ct - re

    out_num_words = len(response.choices[0].message.content.strip().split())

    out = f"Call returned {out_num_words:,} output words"
    if t0 != 0:
        out += f" and took { time.time() - t0 :.1f} seconds"
    else:
        out += "\n"


    out += f"\nToken Usage: (prompt: {pt:5,d})  (reasoning:  {re:,})  (out-calc: {calc_output:,})"
    out += f"\n             (total:  {tt:5,d})  (completion: {ct:,})"


    price_per_million = 0.05
    est1000cost = tt / (price_per_million * 1000000)
    out += f"\nGiven a cost of ($ {price_per_million} per million tokens), estimated cost to make this call 1000 times is ${est1000cost:.2f}"
    
    return out

"""
cost per SKU  - I want to save 1 million

build a configurator for a system to generate a quote and config.  Checked the price list every time... pricelist changes once a quarter...


"""