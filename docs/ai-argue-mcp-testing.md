# AI Argue MCP server: how to test it

*Written 2026-10-28. The server is `mcp/server.py`; build and deploy notes are in `ai-argue-mcp-build.md`.*

## Three places to test, with the same commands

The only thing that changes is the URL, held in `MCP_URL`:

| Where | What it proves | `MCP_URL` | Run the tests from |
|---|---|---|---|
| **poe, local** | The code works | `http://127.0.0.1:8000/mcp` | poe, with the server running in another terminal |
| **walle, behind Nginx** | The service runs on walle | `http://127.0.0.1:8000/mcp` | walle (`ssh walle` first) |
| **Public** | The whole chain (internet → Nginx → service → database) | `https://apps.databloom.net/mcp` | poe, or anywhere |

`127.0.0.1` always means "this machine". On walle it reaches walle's own service, so you must be logged in there. The public URL works only after Nginx is configured.

## Step 1: start the server (poe, local test only)

On walle, systemd runs the server for you, so skip this step there.

```
cd ~/Dropbox/projects/databloom_codes/mcp
.venv/bin/python server.py
```

Wait for `Uvicorn running on http://127.0.0.1:8000`. Leave this terminal running; Ctrl-C stops the server.

## Step 2: set up the helpers (once per terminal window)

Pick the URL for where you're testing:

```
MCP_URL=http://127.0.0.1:8000/mcp
```
or
```
MCP_URL=https://apps.databloom.net/mcp
```

Then paste both helpers:

```
mcpcall() { curl -s -X POST "$MCP_URL" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2025-06-18' -d "$1" | python3 -m json.tool; }
mcptool() { mcpcall "{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":${2:-{\}}}}" | python3 -c 'import sys,json; print(json.dumps(json.loads(json.load(sys.stdin)["result"]["content"][0]["text"]), indent=2))'; }
```

- **`mcpcall`** sends any raw MCP request and pretty-prints the reply.
- **`mcptool`** calls one tool and unwraps the result, so you see clean JSON instead of the escaped `"text"` string.

## Step 3: run the tests

| Test | Command | Expect |
|---|---|---|
| Handshake | `mcpcall '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'` | The server name `ai-argue`, its instructions and capabilities |
| Tool list | `mcpcall '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \| grep '"name"'` | `dataset_info`, `list_debates`, `get_debate`, `query_stats` |
| Headline | `mcptool query_stats '{"name":"judge_stability"}'` | S1 and S1-inv, each `a_wins: 0`, `b_wins: 20` |
| Overview | `mcptool dataset_info` | 91 raw rows, 80 latest, both batches |
| Filter | `mcptool list_debates '{"batch_id":"batch2","limit":2}'` | Two S1-inv rows |
| One debate | `mcptool get_debate '{"run_id":"PASTE-RUN-ID"}'` | The full ruling and transcript, `is_latest: true` |
| Bad input | `mcptool query_stats '{"name":"nope"}'` | An error listing the valid names |

The numbers should match `docs/ai-argue-results-2026-10-27.md`. If they don't, the server is reading a different copy of `debates.db`. On walle that usually means a `git pull` was missed.

## Visual option: the MCP Inspector (poe)

```
npx @modelcontextprotocol/inspector
```

The browser opens. If it doesn't, copy the full address printed in the terminal, including the token.
1. Transport: **Streamable HTTP**.
2. URL: `http://127.0.0.1:8000/mcp` for a local test, or `https://apps.databloom.net/mcp` for the public one.
3. **Connect**, then **Tools → List Tools**, pick a tool, fill in the form, and **Run Tool**.
4. The **History** panel shows the raw JSON of every request and reply.

## When something fails

| Symptom | Likely cause |
|---|---|
| `Connection refused` (local) | The server isn't running. On poe, check step 1. On walle, run `systemctl status databloom-mcp`. |
| `Invalid Host header` / HTTP 421 | The request's Host header isn't in `allowed_hosts` in `server.py` |
| HTTP 404 (public URL) | The Nginx `location /mcp` block is missing, or in the wrong server block |
| HTTP 502 (public URL) | Nginx is up but the service isn't. On walle: `systemctl status databloom-mcp`, then `journalctl -u databloom-mcp -n 40 --no-pager` |
| HTTP 503 (public URL) | The rate limit was hit; wait a minute |
| A plain GET to `/mcp` hangs | Normal. MCP holds an event stream open for GETs. Test with the POST requests above. |
| `command not found: mcpcall` | The helpers aren't defined in this terminal. Repeat step 2. |
