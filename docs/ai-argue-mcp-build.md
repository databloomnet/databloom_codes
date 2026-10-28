# AI Argue MCP server: build brief for Claude Code

*2026-10-28. Written by the databloom-apps planning thread. Read `CLAUDE.md` first, especially the walle section: Python 3.11 on walle, never read or print `.env`.*

**Goal:** a public, read-only MCP server over the curated AI Argue dataset, at `https://apps.databloom.net/mcp`, that anyone can add to Claude as a custom connector.

---

## Part A: the server (local, on poe)

- New top-level folder `mcp/`, alongside `streamlit/` and `gradio/`. Give it its own `requirements.txt` (the official `mcp` Python SDK, pinned) and its own venv.
- `mcp/server.py` uses `FastMCP` from the official SDK with the **streamable HTTP** transport, bound to **127.0.0.1:8000** at path **`/mcp`**. Use stateless mode with JSON responses if the installed SDK supports them; that's simplest behind Nginx. Check the actual API of the installed SDK version rather than assuming it.
- Data: open `../streamlit/data/debates.db` **read-only** (`file:...?mode=ro`, `uri=True`), with a new connection per call. Resolve the path relative to `server.py`. Unless a tool is asked for raw history, use the **latest row per (batch_id, condition, rep)**, the same rule as the results doc.
- Tools (docstrings matter, because they are what the model reads):
  1. `dataset_info()`: the row count, batches, conditions with their models and word budgets, the column meanings, the seat convention (A argues *for* and speaks first; B argues *against*), and GitHub links to both pre-registrations and `docs/ai-argue-results-2026-10-27.md`.
  2. `list_debates(batch_id=None, condition=None, model=None, judge=None, winner=None, limit=50)`: summary rows only, no transcripts. `model` matches either seat. Cap `limit` at 200.
  3. `get_debate(run_id)`: one row, including the ruling text and the parsed transcript.
  4. `query_stats(name)`: named aggregations returning tidy JSON:
     - `seat_bias`: A/B wins per condition, plus the identical-debater totals (S1 and S1-inv).
     - `judge_stability`: S1 and S1-inv distributions.
     - `wordcap_effect`: the weaker model's win rate at equal budgets (C0) against a 4× budget (H1), split by seat.
     - `model_strength_matrix`: model × word budget × seat → win rate and n.
     - An unknown name returns the list of valid names.
- No write tools, and no access to `web_runs.db`.
- **Test locally** with the MCP Inspector (`npx @modelcontextprotocol/inspector`), or a curl `initialize` + `tools/list` against `http://127.0.0.1:8000/mcp`. Then commit and push.

## Part B: deploy files (in the repo, applied on walle by Jeremy)

Create these in `mcp/deploy/`, but **don't install them on walle yourself**. Jeremy runs the install commands in Part C.

- `databloom-mcp.service`: `User=ec2-user`, `WorkingDirectory=/home/ec2-user/apps/mcp`, `ExecStart=/home/ec2-user/apps/mcp/.venv/bin/python server.py`, `Restart=on-failure`, `After=network.target`.
- `nginx-mcp-ratelimit.conf` (http context): `limit_req_zone $binary_remote_addr zone=mcp:1m rate=30r/m;`
- `nginx-mcp-location.conf` (the `apps.databloom.net` server block on 443):
  ```
  location /mcp {
      limit_req zone=mcp burst=20 nodelay;
      proxy_pass http://127.0.0.1:8000/mcp;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_buffering off;
      proxy_cache off;
      proxy_read_timeout 300s;
  }
  ```
- **Known gotcha:** recent MCP SDK versions have DNS-rebinding protection that rejects unexpected `Host` headers, typically with a 421 or "Invalid Host header" error. Behind Nginx the Host is `apps.databloom.net`. Configure the server's allowed hosts to include it (and `127.0.0.1:8000` for local tests) rather than disabling the protection.

## Part C: install on walle (Jeremy runs these, one at a time)

```
ssh walle
cd ~/apps && git pull
python3.11 -m venv mcp/.venv
mcp/.venv/bin/pip install -r mcp/requirements.txt
sudo cp mcp/deploy/databloom-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now databloom-mcp
curl -s -X POST http://127.0.0.1:8000/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```
Then Nginx. Find the file holding the `apps.databloom.net` server block, back it up, and edit it:
```
sudo grep -l "server_name apps.databloom.net" /etc/nginx/conf.d/* /etc/nginx/nginx.conf
sudo cp <that file> <that file>.bak-2026-10-28
sudo cp mcp/deploy/nginx-mcp-ratelimit.conf /etc/nginx/conf.d/
sudo nano <that file>        # paste the location block inside the 443 server block for apps.databloom.net
sudo nginx -t && sudo systemctl reload nginx
```
Only reload if `nginx -t` passes. If anything breaks, copy the `.bak` back and reload.

Final check from poe: run the same curl against `https://apps.databloom.net/mcp`.

## Part D: record it

- `CLAUDE.md`, walle section: the third service (`databloom-mcp`, port 8000, venv `~/apps/mcp/.venv`) and the deploy line `sudo systemctl restart databloom-mcp`.
- The planning thread updates the runbook.
