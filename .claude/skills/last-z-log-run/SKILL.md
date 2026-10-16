---
name: last-z-log-run
description: Log a finished Last Z task run to the local dashboard and notify the user. Every Last Z task skill ends by following this skill, including runs that stopped early. Also use when asked to check or fix the Last Z run log.
---

# Log a Last Z run

Run this at the end of every Last Z task, even when the task stopped early or failed. A partial run still gets logged.

## 1. Find the workspace

The workspace is the folder that holds `CLAUDE.md`, `dashboard/` and `data/`. It is usually `~/Last-Z-Tasks`.

- In Claude Code it's the current folder.
- In a Claude Desktop or cloud session linked to the Mac, it's the connected folder, reached with the device tools (`device_bash` at `$HOME/mnt/<folder-name>`).

If you can't reach the workspace, give the run summary in chat, say it wasn't logged, and skip to step 4.

## 2. Append one line to `data/runs.js`

`data/runs.js` is the log. Its first line is `window.LZ_RUNS = window.LZ_RUNS || [];` and each run after that is one line:

```js
LZ_RUNS.push({"id":"2026-10-16T11:17-running-boomers","date":"2026-10-16","time":"11:17","task":"running-boomers","label":"Running Boomers","settings":{"level":49},"requested":10,"completed":10,"status":"complete","minutes":5,"resources":{"fuel":{"before":256,"after":96}},"issues":["1 formations-busy wait","1 misclick opened Chat"],"notes":""});
```

Field rules:

| Field | Value |
|---|---|
| `id` | `<date>T<time>-<task>` |
| `date`, `time` | When the run **started**, in the user's local time. `YYYY-MM-DD` and 24h `HH:MM`. |
| `task` | The task skill's slug, without the `last-z-` prefix |
| `label` | Human name of the task |
| `settings` | What the user chose, e.g. `{"level":49}` |
| `requested` | How many units the user asked for (rallies, gathers, etc.) |
| `completed` | How many you **verified**. Never count a click as a completion. |
| `status` | `complete` (completed = requested), `partial` (stopped early), or `failed` (nothing completed) |
| `minutes` | Rounded run length |
| `resources` | Anything spent, each with `before` and `after` as read on screen. Omit a value you didn't see. Don't guess. |
| `issues` | Short phrases for errors, waits, misclicks, warnings. `[]` if none. |
| `notes` | Anything else worth keeping, or `""` |

How to write it:

- Append only. Never rewrite or reorder existing lines.
- Keep it one line of valid JSON inside `LZ_RUNS.push(...);`: double quotes, no trailing commas, no comments.
- If `data/runs.js` is missing, create it with the header line first.
- Check that the file still parses after writing. If `python3` is available:

  ```bash
  python3 - <<'EOF'
  import json
  for i, line in enumerate(open("data/runs.js"), 1):
      line = line.strip()
      if line.startswith("LZ_RUNS.push(") and line.endswith(");"):
          json.loads(line[len("LZ_RUNS.push("):-2])
      elif line and not line.startswith("window.LZ_RUNS"):
          raise SystemExit(f"bad line {i}")
  print("ok")
  EOF
  ```

  If the check fails on the line you just wrote, fix that line. Don't touch other lines without asking.

## 3. Point to the dashboard

Tell the user the run was logged and that `dashboard/index.html` shows it. The page reloads itself every minute while it's open.

## 4. Notify

If a `PushNotification` tool is available, send one line under 200 characters that leads with the result, for example:

`Boomers done: 10/10 Lv49 rallies, fuel 256→96, 5 min. 1 busy wait.`

For a partial or failed run, lead with what went wrong and how many got done:

`Boomers stopped at 6/10: out of fuel, refill needs diamonds.`

The tool decides whether to send. If it says it wasn't sent, that's fine. Don't retry.

## Checking or fixing the log

When the user asks to check the run log, or the dashboard says the log is broken or skipped entries:

1. Run the check from step 2. Also flag any `push` line whose object has no `task` or no `date` in `YYYY-MM-DD` form, since the dashboard skips those.
2. Show the user each bad line and the fix you'd make.
3. Change only those lines, and only after the user says yes. Then run the check again.
