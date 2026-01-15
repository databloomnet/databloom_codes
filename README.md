# DataBloom Apps

This repository contains the application code for DataBloom.net demo apps.

## Structure

```
apps/
├── streamlit/
│   ├── app.py
│   ├── pages/
│   └── requirements.txt
└── gradio/
    ├── app.py
    └── requirements.txt
```


- **Streamlit app** is served at `https://apps.databloom.net`
- **Gradio app** is served at `https://gradio.apps.databloom.net`

Both apps run on a single EC2 instance behind Nginx and are managed by systemd.

---

## Local Development (Recommended)

**Use Python 3.12 locally.**

Some dependencies (e.g. NumPy) do not yet support Python 3.13, and production currently runs on Python 3.12-compatible packages.

### Prerequisites
- Python **3.12**
- [`uv`](https://github.com/astral-sh/uv)

---

## Streamlit (local)

```bash
cd streamlit
uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run app.py
```

Open: http://localhost:8501

---

## Gradio (local)

```bash
cd gradio
uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
python app.py
```

Open: http://localhost:7860

---

## Deployment Notes

- Virtual environments (`.venv`) are **not committed**
- `requirements.txt` files are the source of truth for dependencies
- Services on EC2 are restarted after deploy:

```bash
sudo systemctl restart streamlit
sudo systemctl restart gradio-demo
```

---

## Workflow Summary

1. Develop locally on your laptop
2. Commit and push to GitHub
3. Pull changes on EC2
4. Restart services
