# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataBloom.net demo apps — a portfolio of AI/GenAI and Python demos by Jeremy Bloom. Two web apps (Streamlit and Gradio) run on a single EC2 instance behind Nginx, managed by systemd.

- **Streamlit app**: https://apps.databloom.net
- **Gradio app**: https://gradio.apps.databloom.net

## Development Commands

**Prerequisites:** Python 3.12 and [uv](https://github.com/astral-sh/uv). Python 3.13 is not supported (NumPy compatibility).

### Streamlit
```bash
cd streamlit
uv venv -p 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run app.py                    # runs on http://localhost:8501
```

### Gradio
```bash
cd gradio
uv venv -p 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python app.py                           # runs on http://localhost:7860
```

### Tests
```bash
cd streamlit
pytest pages/test_benchmark_problems.py
```

### Deployment (on EC2)
```bash
sudo systemctl restart streamlit
sudo systemctl restart gradio-demo
```

## Architecture

### Streamlit App (`streamlit/`)
Multi-page Streamlit app. `app.py` is the entry point; pages live in `pages/` with numeric prefixes controlling sidebar order (001–012). Pages range from utility demos (logger, timer) to AI-powered features (chat, debate, benchmarking).

**Core modules:**
- `chatting.py` — Unified LLM interface. `chat_with_llm()` routes to provider-specific functions (`chat_with_gpt()`, `chat_with_anthropic()`) based on model name prefix.
- `support.py` — Model enumeration; defines available models per provider.
- `rate_limiter.py` — Sliding-window rate limiter using `deque`. Stored in `st.session_state`.
- `response_parser.py` — Whitelist-based field extraction from API responses (prevents leaking sensitive data). Includes token usage and cost estimation.
- `logger.py` — Session-aware logging with UUID-based session IDs. Writes to `app.log`.

**LLM providers supported:** OpenAI, Anthropic, plus alternatives via environment keys (Gemini, DeepSeek, Groq, Grok, OpenRouter).

### Gradio App (`gradio/`)
Minimal starter app — a single `app.py` with a hello-world `Interface`.

## Key Patterns

- **API keys** are loaded from `streamlit/.env` via `python-dotenv`. Keys exist for OpenAI, Anthropic, Gemini, DeepSeek, Groq, Grok, and OpenRouter.
- **Session state** is managed through `st.session_state` for rate limiters, conversation history, and session IDs.
- **Dependencies** are managed with `uv`. `requirements.txt` is the source of truth; `pyproject.toml` and `uv.lock` also exist per app.
- Each Streamlit page links back to its GitHub source for educational purposes.
- `benchmark_problems.json` contains structured logic puzzles (with difficulty levels and categories) used by `011_ai_benchmark.py` for LLM evaluation.
