---
name: last-z-log-run
description: Log a finished Last Z task run to data/runs.json, sync it to the user's claude.ai dashboard, open the dashboard in the chat and notify the user. Every Last Z task skill ends with this, including runs that stopped early. Also use when asked to open, sync, check or fix the Last Z dashboard or run log.
---

# Log a Last Z run

Run this at the end of every Last Z task, even when the task stopped early or failed. A partial run still gets logged.

Runs live in two places:

- **`data/runs.json`** in the workspace: the log, and the source of truth.
- **The claude.ai dashboard** ("Last Z Tasks"): what the user looks at, in the Claude app on their computer or phone. Its link is `dashboard_url` in `data/config.json`. It reads runs from its own database, which this skill keeps identical to `data/runs.json`.

Never try to open `dashboard/index.html` or any `file://` path in a browser. The browsers Claude can drive can't open files from the user's computer. The dashboard is opened only with the Artifact tool (step 4).

## 1. Find the workspace

The workspace is the folder that holds `CLAUDE.md` and `data/`. It is usually `~/Last-Z-Tasks`.

- In Claude Code it's the current folder.
- In a Claude Desktop or cloud session linked to the Mac, it's the connected folder, reached with the device tools (`device_bash` at `$HOME/mnt/<folder-name>`).

If you can't reach the workspace, give the run report in chat, say it wasn't logged, and skip to step 5.

## 2. Add the run to `data/runs.json`

The file holds one object with a `runs` array, oldest first, one run per line:

```json
{
  "runs": [
    {"id":"2026-10-16T11:13-running-boomers","date":"2026-10-16","time":"11:13","task":"running-boomers","label":"Running Boomers","short":"Boomers","settings":{"level":49},"requested":10,"completed":10,"status":"complete","minutes":5,"resources":{"fuel":{"before":256,"after":96}},"issues":["1 formations-busy wait"],"notes":""}
  ]
}
```

Field rules:

| Field | Value |
|---|---|
| `id` | `<date>T<time>-<task>` |
| `date`, `time` | When the run **started**, in the user's local time. `YYYY-MM-DD` and 24h `HH:MM`. |
| `task` | The task skill's slug, without the `last-z-` prefix |
| `label` | Human name of the task |
| `short` | One-word name for the dashboard's run rows, e.g. `Boomers` |
| `settings` | What the user chose, e.g. `{"level":49}` |
| `requested` | How many units the user asked for (rallies, gathers, etc.) |
| `completed` | How many you **verified**. Never count a click as a completion. |
| `status` | `complete` (completed = requested), `partial` (stopped early), or `failed` (nothing completed) |
| `minutes` | Rounded run length |
| `resources` | Anything spent, each with `before` and `after` as read on screen. Omit a value you didn't see. Don't guess. |
| `issues` | Short phrases for errors, waits, misclicks, warnings. `[]` if none. |
| `notes` | Anything else worth keeping, or `""` |

Write it with this script from the workspace folder, pasting the run object in place of `RUN_JSON`. It creates the file if it's missing, refuses a duplicate id, keeps one run per line, and never touches earlier runs:

```bash
python3 - <<'EOF'
import json, os
path = "data/runs.json"
run = json.loads(r'''RUN_JSON''')
log = json.load(open(path)) if os.path.exists(path) else {"runs": []}
if any(r.get("id") == run["id"] for r in log["runs"]):
    raise SystemExit("already logged: " + run["id"])
log["runs"].append(run)
text = '{\n  "runs": [\n' + ",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in log["runs"]) + "\n  ]\n}\n"
json.loads(text)  # sanity check before writing
open(path, "w").write(text)
print("logged", run["id"], "-", len(log["runs"]), "runs in the log")
EOF
```

## 3. Sync the claude.ai dashboard

Make the dashboard's database match `data/runs.json` exactly.

1. Read `dashboard_url` from `data/config.json`. If there isn't one, skip this step and mention that "set up Last Z" creates the dashboard.
2. Load the `ArtifactData` tool (ToolSearch `select:ArtifactData`). If this session doesn't have it (for example Claude Code in a terminal), skip this step and say the dashboard will catch up the next time a run is logged from a Claude Desktop chat, or when the user says "sync my Last Z dashboard".
3. `list` the collection `runs` at `dashboard_url`, paging with `query.cursor` until there's no `next_cursor`. Note each document's `id`, data and `version`.
4. For every run in `data/runs.json`:
   - **Not on the dashboard:** write it with `set`, `doc_id` = the run's `id`, `data` = the run object exactly as logged, no `if_version`.
   - **On the dashboard but different:** write it with `set` and that document's `version` as `if_version`.
   - **Identical:** leave it.

   Send the writes as one `batch` (up to 50 per batch).
5. **On the dashboard but not in the log:** don't delete anything on your own. List those runs for the user and delete them (with `if_version`) only if they say so.

The page updates live, so there's nothing to republish.

## 4. Open the dashboard

Open it in the chat with the Artifact tool: `action: "open"`, `url` = `dashboard_url`. It's also in the user's artifacts on claude.ai and in the Claude phone app.

If the Artifact tool isn't available, give the dashboard link as plain text instead. Never open the local file or a `file://` path.

## 5. Notify

If a `PushNotification` tool is available, send one line under 200 characters that leads with the result, for example:

`Boomers done: 10/10 Lv49 rallies, fuel 256→96, 5 min. 1 busy wait.`

For a partial or failed run, lead with what went wrong and how many got done:

`Boomers stopped at 6/10: out of fuel, refill needs diamonds.`

The tool decides whether to send. If it says it wasn't sent, that's fine. Don't retry.

## Other requests

- **"Open my Last Z dashboard":** step 4 on its own.
- **"Sync my Last Z dashboard":** step 3, then step 4.
- **"Check the Last Z run log":**
  1. Load `data/runs.json` with `json.load`. Flag a file that doesn't parse, any run without a `task`, any run without a `date` in `YYYY-MM-DD` form (the dashboard skips those), and any repeated `id`.
  2. Show the user each problem and the fix you'd make.
  3. Change only those runs, and only after the user says yes. Then run step 3 so the dashboard matches.
