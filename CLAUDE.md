# Last Z Tasks workspace

This folder automates tasks in **Last Z: Survival Shooter**. The game runs in BlueStacks Air on the user's Mac, and Claude plays it through computer use.

## What's here

| Path | What it is |
|---|---|
| `.claude/skills/last-z-<task>/SKILL.md` | One folder per game task. Follow the matching skill when the user asks for a task. |
| `.claude/skills/last-z-log-run/` | Shared last step for every task: log the run and notify the user |
| `.claude/skills/last-z-setup/` | First-time setup and health check |
| `data/runs.js` | The user's run log. One `LZ_RUNS.push({...});` line per run. Git-ignored. |
| `dashboard/index.html` | The dashboard. It reads `data/runs.js`; open it in a browser. |

If these skills don't load automatically (for example in a Claude Desktop chat), read the matching `SKILL.md` from this folder directly.

## Tasks

| Ask | Skill |
|---|---|
| "run 10 boomers", "rally Stegosauruses" | `last-z-running-boomers` |

## Rules

- Ask a task's setup questions up front, then run it to the end without more questions. The user may have stepped away.
- Count only completions you verified on screen.
- Every task run ends with `last-z-log-run`, including runs that stopped early.
- Never spend diamonds or real money, and never accept a purchase. Stop and log the run as `partial` instead.
- `data/runs.js` is append-only. Never rewrite or delete past runs unless the user asks.
- Never commit anything in `data/`.

## Adding a task

1. Walk through the task once in the game with the user.
2. Write `.claude/skills/last-z-<task>/SKILL.md` using `last-z-running-boomers` as the model: setup questions, each tap with what to confirm before the next, error handling, then the report and the `last-z-log-run` hand-off.
3. Add a row to the Tasks table above and to the README.
