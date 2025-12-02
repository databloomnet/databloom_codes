# response_parser.py
"""
simple response parsing
"""

import datetime
import streamlit as st
from openai import OpenAI
import time

VALID_KEYS_TOP = ["id", "created",  "model", "object"]
VALID_KEYS_CHOICES_0_MESSAGE = ["content", "refusal"]
VALID_KEYS_USAGE = ["completion_tokens", "prompt_tokens", "total_tokens"]
VALID_KEYS_USAGE_COMPLETION_DETAILS = ["reasoning_tokens"]


def get_approved_completion_to_share(completion, list_of_keys):
    """
    preapproved list of keys we can get from chatgpt resposne
    """
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
        response["warnings"] = warnings
    
    return response



def get_est_response_costSUSPENDED(response, t0 = 0):
    # for now assume chatgpt
    # get specific tokens to est cost withOUT model - so flat est... not great

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




def get_response_summary(completion, list_of_keys = ["created", "model", "id", "object", "content", "refusal", "completion_tokens", "prompt_tokens", "total_tokens", "reasoning_tokens"]):
    # req_params =     completion_approved_to_share = get_response_info(completion, list_of_keys)
    completion_approved_to_share = get_approved_completion_to_share(completion, list_of_keys)
    for k in sorted(completion_approved_to_share.keys()):
        print(k)

    out_list = []

    time_elapsed_since_prompted = -1
    msg_est_cost = ""
    if "created" in completion_approved_to_share:
        time_elapsed_since_prompted = time.time() - completion.created
        out_list.append("Completion initiated {:.1f}s ago".format(time_elapsed_since_prompted))
        print("com")

    

    # est cost based on model
    model_to_token_cost_d = { # (input toekns, output tokens)
        "gpt-5-nano": (0.05, 0.40),
        "gpt-5-mini": (0.25, 2.00),
    }

    model = completion.model 
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens

    prompt_tokens__est_cost_per_million = 0
    completion_tokens__est_cost_per_million = 0
    for prefix in model_to_token_cost_d:
        if model.startswith(prefix):
            prompt_tokens__est_cost_per_million, completion_tokens__est_cost_per_million = model_to_token_cost_d[prefix]

    if prompt_tokens__est_cost_per_million and completion_tokens__est_cost_per_million:
        cost = (prompt_tokens * prompt_tokens__est_cost_per_million) + (completion_tokens * completion_tokens__est_cost_per_million)
        cost /= 1000000 
        m = "est cost: {:0.5f}   (or {:.5f} per 1000 calls)".format(cost, cost * 1000)
    else:
        m = "could not identify model, can't estimate cost"
    out_list.append(m)




    for k in completion_approved_to_share:
        out_list.append(" {:20s}   {:}".format(k, completion_approved_to_share[k]))

    print(len(out_list))
    return "\n".join(out_list)



