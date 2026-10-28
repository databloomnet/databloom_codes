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

### Deployment (EC2 host `walle`)
Deploy is git-based. Nothing is copied from the Mac directly.
```bash
git push                                          # from the Mac
ssh walle 'cd ~/apps && git pull && sudo systemctl restart streamlit'   # or gradio-demo
```

**walle differs from local dev:**
- The repo is at `/home/ec2-user/apps`. API keys are in `~/apps/.env`, at the repo root; `load_dotenv()` finds it by searching upward from each page. Never read, print or copy `.env`.
- The Streamlit venv is `~/apps/.venv` (repo root, **Python 3.11**, plain pip, no uv). Gradio has its own at `~/apps/gradio/.venv`.
- Local dev is 3.12, so **avoid 3.12-only syntax** (for example PEP 701 nested f-string quotes, or the `type X = ...` statement): it works locally and breaks in production.
- `git pull` does not install dependencies. After a `requirements.txt` change, run `ssh walle '~/apps/.venv/bin/pip install -r ~/apps/streamlit/requirements.txt'` before restarting.
- **A third service, `databloom-mcp`,** serves the AI Argue MCP server: `~/apps/mcp`, its own venv `~/apps/mcp/.venv`, `127.0.0.1:8000/mcp`, public at `https://apps.databloom.net/mcp` through Nginx. After changing `mcp/server.py` or `streamlit/data/debates.db`, also run `sudo systemctl restart databloom-mcp`. Test it with `docs/ai-argue-mcp-testing.md`.
- The systemd config that actually runs is the drop-in `/etc/systemd/system/<unit>.service.d/override.conf`. The base units are stale.
- Page URL slugs are set by `url_path=` in `streamlit/app.py`, and databloom.net deep-links to them (see the runbook §8). Don't change one without flagging it.

## Architecture

### Streamlit App (`streamlit/`)
Multi-page Streamlit app using `st.navigation` for sidebar navigation with sections. `app.py` is the entry point and navigation router; it calls `st.set_page_config`, initializes the rate limiter, and declares all pages via `st.Page` grouped into sections ("AI Apps", "Tools"). Pages live in `pages/` with numeric prefixes. The home page is `pages/home.py` (registered with `default=True`).

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
