# support.py

# wikipedia-playground.py

import streamlit as st
import datetime
import time
from dotenv import load_dotenv
import os
import wikipedia

from rate_limiter import RateLimiter
from openai import OpenAI
from anthropic import Anthropic
from response_parser import get_response_summary

#LLM_INPUT_CHAR_LIMIT = 2000


load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def get_anthropic_model_list(show_all = False):
    """
    haiku is fastest and cheapest
    sonnet balanced
    opus intelligent and powerful
    """
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    models_list = []

    try:
        models = client.models.list()
    except Exception as e:
        print(f"Error listing models: {e}")

    for model in models.data:
        if show_all:
            models_list.append(model.id)
        else:
            models_list.append(model.id)
            
            pass
            #model_id = model.id 
            #if not model_id.startswith("gpt-"):

    return models_list


def get_openai_model_list(show_all = False):
    client = OpenAI(api_key=OPENAI_API_KEY)

    models_list = []

    try:
        models = client.models.list()

    except Exception as e:
        print(f"An error occurred: {e}")



    for model in models.data:
        if show_all:
            models_list.append(model.id)
        else:
            model_id = model.id 
            if not model_id.startswith("gpt-"):
                continue

            skip_terms = ["latest", "pro", "2025", "2024", "transcribe", "preview", "search", "image", "realtime", "codex", "audio", "realtime", "turbo", "tts"]
            skip = False
            for term in skip_terms:
                if term in model_id:
                    skip = True
                    break
            if skip:
                continue

            models_list.append(model_id)


    return models_list

models_list = get_openai_model_list()
for x in sorted(models_list):
    print( x )

models_list = get_anthropic_model_list()
for x in models_list:
    print( x)
