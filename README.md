# Last Z Tasks

Claude runs repeatable tasks in **Last Z: Survival Shooter** for you, logs each run, and shows your history on a dashboard you can open on your computer, your phone or in the Claude app.

- The game runs in BlueStacks Air on a Mac, and Claude plays it with computer use.
- You answer a few questions at the start of a task, then you can walk away.
- When the task finishes, it's added to both dashboards and Claude can send a one-line summary to your phone.

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

Either way, Claude copies the task files, creates your run log, checks that it can see BlueStacks, and sets up your two dashboards. The claude.ai dashboard needs Claude Desktop (or claude.ai), so if you set up from Claude Code, run `set up Last Z` once from a Claude Desktop chat with the folder added to get it.

## Using it

| Say | What happens |
|---|---|
| `run 10 boomers` | Runs 10 Stegosaurus rallies, logs the run, and notifies you |
| `log alliance stats` | Reads your tracked alliance members' stats, updates your stats spreadsheet, and republishes your alliance page |
| `update Last Z Tasks` | Pulls the latest task files and refreshes your claude.ai dashboard's design. Your run history is never touched. |
| `sync the Last Z dashboard` | Copies any runs the claude.ai dashboard is missing from your log |
| `check the Last Z run log` | Finds and fixes broken log entries |

**Your dashboards**

- **On your computer:** open `Last-Z-Tasks/dashboard/index.html` in your web browser (from Finder: right-click → Open With → Chrome or Safari). It reloads every minute, so you can leave it open. It won't load inside another app's file preview, because it reads your log from the folder next to it.
- **On your phone or in the Claude app:** your private **Last Z Tasks** page on claude.ai. It updates live after every run. Pin it for quick access.

**Before you step away:** keep the Mac awake and unlocked, and leave the Claude app and BlueStacks open. Computer use stops when the screen locks or the Mac sleeps.

## Tasks

| Task | Skill | Status |
|---|---|---|
| Running Boomers (Stegosaurus rallies) | [last-z-running-boomers](.claude/skills/last-z-running-boomers/SKILL.md) | Tested 2026-10-16: 10/10 level-49 rallies |
| Alliance Stats (member power tracking) | [last-z-alliance-stats](.claude/skills/last-z-alliance-stats/SKILL.md) | Tested 2026-10-16: 14 R1/R2 members captured |

## Alliance stats page

`last-z-alliance-stats` keeps a spreadsheet of your tracked members (`data/Last Z Alliance Stats.xlsx`) with three tabs: Member Stats (every capture, with the change from the one before), Member Reference (who to track) and Summary (rankings by % change, plus a watchlist of slow growers). It also exports `alliance/data/alliance.js` for `alliance/index.html`, a page you can share with your alliance's leaders.

To put the page online, make a small GitHub repo holding `index.html` and `data/alliance.js`, import it into Vercel (Framework: Other, no build command), and add it to `data/config.json`:

```json
{"alliance": {"tag": "RfC", "name": "RebornFromChaos", "state": "644"},
 "alliance_site_repo": "you/your-alliance-site",
 "alliance_site_url": "https://your-alliance-site.vercel.app"}
```

After each capture, the skill pushes the new data file to that repo and Vercel republishes the page.

## How it's built

```
Last-Z-Tasks/
  CLAUDE.md                   ← workspace rules Claude follows
  .claude/skills/
    last-z-setup/             ← setup and health check
    last-z-log-run/           ← shared last step: log the run, notify
    last-z-running-boomers/   ← one folder per task
  dashboard/index.html        ← the dashboard (local, and the template for claude.ai)
  alliance/index.html         ← the alliance stats page (reads alliance/data/alliance.js)
  data/runs.js                ← your run log (stays on your computer)
  data/config.json            ← your settings, like your claude.ai dashboard link
```

- Skills live in `.claude/skills/`, so Claude Code loads them automatically. In Claude Desktop, `CLAUDE.md` points Claude to them.
- The run log is a JavaScript file with one `LZ_RUNS.push({...});` line per run. The dashboard loads it directly, so it works by double-click with no server.
- The same `dashboard/index.html` is published to claude.ai as each user's private dashboard. There it reads runs from the page's own database, and the log step copies each new run into it, filling in any it missed.
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
