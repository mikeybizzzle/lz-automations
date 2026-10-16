# Last Z Tasks

Claude runs repeatable tasks in **Last Z: Survival Shooter** for you, logs each run, and shows your history on a private dashboard in the Claude app, on your computer or your phone.

- The game runs in BlueStacks Air on a Mac, and Claude plays it with computer use.
- You answer a few questions at the start of a task, then you can walk away.
- When the task finishes, Claude logs it, opens your dashboard in the chat and can send a one-line summary to your phone.

## What you need

- A Mac with BlueStacks Air and Last Z installed
- The Claude desktop app, signed in, with computer use turned on (Settings → This computer → Computer use)
- Optional: Claude Code, if you'd rather work from the terminal

## Setup (about 2 minutes)

**In Claude Desktop**

1. Create a folder named `Last-Z-Tasks` in your home folder.
2. Start a new chat, then add that folder with **+** → **Add folder**.
3. Send:
   > Set up Last Z Tasks in this folder from https://github.com/mikeybizzzle/lz-automations

**In Claude Code**

```bash
git clone https://github.com/mikeybizzzle/lz-automations ~/Last-Z-Tasks
cd ~/Last-Z-Tasks && claude
```

Then send: `set up Last Z`

Either way, Claude copies the task files, creates your run log, checks that it can see BlueStacks, and creates your dashboard. The dashboard lives on claude.ai, so if you set up from Claude Code, run `set up Last Z` once from a Claude Desktop chat with the folder added to create it.

## Using it

| Say | What happens |
|---|---|
| `run 10 boomers` | Runs 10 Stegosaurus rallies, logs the run, and notifies you |
| `open my Last Z dashboard` | Opens your dashboard in the chat |
| `update Last Z Tasks` | Pulls the latest task files and refreshes your dashboard's design. Your run history is never touched. |
| `sync my Last Z dashboard` | Makes your dashboard match your log exactly |
| `check the Last Z run log` | Finds and fixes broken log entries |

**Your dashboard** is a private page on claude.ai. It opens in the chat after every run, and it's in your artifacts in the Claude app on your phone. Pin it for quick access.

**Before you step away:** keep the Mac awake and unlocked, and leave the Claude app and BlueStacks open. Computer use stops when the screen locks or the Mac sleeps.

## Tasks

| Task | Skill | Status |
|---|---|---|
| Running Boomers (Stegosaurus rallies) | [last-z-running-boomers](.claude/skills/last-z-running-boomers/SKILL.md) | Tested 2026-10-16: 10/10 level-49 rallies |

## How it's built

```
Last-Z-Tasks/
  CLAUDE.md                   ← workspace rules Claude follows
  .claude/skills/
    last-z-setup/             ← setup and health check
    last-z-log-run/           ← shared last step: log the run, notify
    last-z-running-boomers/   ← one folder per task
  dashboard/index.html        ← the dashboard template, published to claude.ai
  data/runs.json              ← your run log (stays on your computer)
  data/config.json            ← your settings, like your dashboard link
```

- Skills live in `.claude/skills/`, so Claude Code loads them automatically. In Claude Desktop, `CLAUDE.md` points Claude to them.
- The run log is `data/runs.json`, one run per line. It's the source of truth.
- `dashboard/index.html` is published to claude.ai as each user's private dashboard. It reads runs from the page's own database, and after every run Claude makes that database match `data/runs.json` exactly, then opens the dashboard in the chat.
- `data/` is git-ignored, so each person's history stays private and updates never overwrite it.

## Adding a task

1. Walk Claude through the task once in the game.
2. Have Claude write `.claude/skills/last-z-<task>/SKILL.md`, modeled on the Boomers skill. It should cover:
   - the setup questions to ask
   - each tap, with what to confirm before the next one
   - how to handle errors
   - the `last-z-log-run` step at the end
3. Test it with a live run, then add a row to the Tasks table here and in `CLAUDE.md`.

Tasks never spend diamonds or real money. Anything that would gets stopped and logged.
