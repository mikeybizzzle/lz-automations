---
name: last-z-setup
description: Set up or check the Last Z Tasks workspace (task skills, run log, dashboard) on the user's Mac. Use when asked to set up Last Z, install Last Z Tasks, or when a Last Z task can't find its workspace.
---

# Set up Last Z Tasks

Goal: the user ends up with a `Last-Z-Tasks` folder on their Mac that holds the task skills, an empty run log, and a dashboard they can open. Safe to run again: it never overwrites existing run data.

Repo: `https://github.com/mikeybizzzle/lz-automations`

## 1. Get the workspace onto the Mac

Check which situation you're in:

**A. You're already inside a copy.** The current or connected folder contains `CLAUDE.md` and `dashboard/index.html`. Skip to step 2.

**B. Claude Code running on the Mac.** Clone into `~/Last-Z-Tasks` unless the user named another place:

```bash
git clone https://github.com/mikeybizzzle/lz-automations ~/Last-Z-Tasks
```

If git isn't installed, download `https://github.com/mikeybizzzle/lz-automations/archive/refs/heads/main.zip` and unzip it there instead. Then tell the user to restart Claude Code from that folder (`cd ~/Last-Z-Tasks && claude`) so the task skills load.

**C. Claude Desktop, or a cloud session linked to the Mac.**

- If no folder is connected, ask the user to create a folder named `Last-Z-Tasks` in their home folder and add it to the chat (the **+** menu → **Add folder**). Wait until it's connected.
- Clone into the connected folder with `device_bash`:

  ```bash
  cd "$HOME/mnt/Last-Z-Tasks" && git clone https://github.com/mikeybizzzle/lz-automations .
  ```

  If the folder isn't empty, clone to a temp folder inside it, move the contents up, and leave existing files alone. If the network blocks GitHub, ask the user to download the repo zip from GitHub and unzip it into the folder.

## 2. Create the run log

If `data/runs.js` doesn't exist, create it with exactly this one line:

```js
window.LZ_RUNS = window.LZ_RUNS || [];
```

If it already exists, leave it as is and count the lines starting with `LZ_RUNS.push(` to report how many runs are logged.

`data/` is git-ignored, so updating the workspace with `git pull` never touches the log.

## 3. Check the game connection

- Resolve and request computer-use access to **BlueStacks** (`com.now.gg.BlueStacks`). If computer use isn't available, tell the user it needs the Claude desktop app open on the Mac with computer use turned on (Settings → This computer → Computer use).
- Take one screenshot to confirm the game is visible. Don't tap anything.

## 4. Show the dashboard

- In Claude Code on the Mac: `open dashboard/index.html`
- Otherwise: tell the user to double-click `Last-Z-Tasks/dashboard/index.html` in Finder. Suggest they bookmark it in their browser.

## 5. Tell the user how to use it

Keep it short:

- **Run a task:** for example, "run 10 boomers." Claude asks its setup questions first, then runs the task without needing them.
- **Step away safely:** keep the Mac awake and unlocked, and keep the Claude desktop app and BlueStacks open. Computer use can't work while the screen is locked or the Mac is asleep. Turning off auto-lock and sleep in System Settings for the duration of a run is enough.
- **Phone alerts:** when a task ends, Claude sends a one-line summary if the session has notifications. In Claude Code that's a desktop notification, which also reaches the phone when Remote Control is on. Without notifications, the summary waits in the chat and on the dashboard.
- **Update tasks:** "update Last Z Tasks" runs `git pull` in the folder.
- **Available tasks:** list the task skills in `.claude/skills/` (skip `last-z-setup` and `last-z-log-run`).
