---
name: last-z-setup
description: Set up, update or check the Last Z Tasks workspace (task skills, run log, local and claude.ai dashboards) on the user's Mac. Use when asked to set up or update Last Z, install Last Z Tasks, or when a Last Z task can't find its workspace.
---

# Set up Last Z Tasks

Goal: the user ends up with a `Last-Z-Tasks` folder on their Mac that holds the task skills and an empty run log, plus two views of the same dashboard: one they open from the folder, and one on claude.ai they can open on their phone or in the Claude app. Safe to run again: it never overwrites existing run data or creates a second claude.ai dashboard.

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

## 4. Create the claude.ai dashboard

The template is **`dashboard/index.html`** in the workspace. It's the same file as the local dashboard: on claude.ai it reads runs from the page's own database instead of `data/runs.js`. Every user publishes their own private copy.

1. **Already set up?** If `data/config.json` has a `dashboard_url`, `read` it with the Artifact tool to confirm it still exists, then go straight to **Sync** below. If it's gone, continue.
2. **Found an existing one?** `list` the user's artifacts and look for one titled "Last Z Tasks". If there is one, ask whether to use it. If yes, skip publishing and go to **Save the link**.
3. **Publish** `dashboard/index.html` with the Artifact tool:
   - `capabilities`: `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}}` (anyone the user shares it with can read; only the user writes)
   - `icon`: `chart`
   - `description`: `Live log of my automated Last Z runs: daily totals, task breakdowns and every run's details.`

   The Artifact tool publishes from a file in this session's own working or scratchpad folder. If the workspace is only reachable on the Mac (a cloud session), stage `dashboard/index.html` with `device_stage_files`, copy it into the scratchpad, and publish that copy.
4. **Save the link** to `data/config.json` as `{"dashboard_url": "<url>"}`, keeping any other keys already there. `data/` is git-ignored, so the link stays private.
5. **Sync** existing runs: follow step 3 of **last-z-log-run**.
6. Offer once to pin it to the user's sidebar. It's private until they share it from the page's Share menu.

If this session has no Artifact tool (Claude Code in a terminal, for example), skip this step and tell the user to run "set up Last Z" once from a Claude Desktop chat with the folder connected to add the phone dashboard.

## 5. Show the local dashboard

- In Claude Code on the Mac: `open dashboard/index.html`
- Otherwise: tell the user to open `Last-Z-Tasks/dashboard/index.html` from Finder in their web browser (double-click, or right-click → Open With → Chrome or Safari). Opening it inside another app's file preview doesn't work, because the page has to load `data/runs.js` from the folder next to it.

## 6. Tell the user how to use it

Keep it short:

- **Run a task:** for example, "run 10 boomers." Claude asks its setup questions first, then runs the task without needing them.
- **Step away safely:** keep the Mac awake and unlocked, and keep the Claude desktop app and BlueStacks open. Computer use can't work while the screen is locked or the Mac is asleep. Turning off auto-lock and sleep in System Settings for the duration of a run is enough.
- **Phone alerts:** when a task ends, Claude sends a one-line summary if the session has notifications. In Claude Code that's a desktop notification, which also reaches the phone when Remote Control is on. Without notifications, the summary waits in the chat and on the dashboard.
- **Dashboards:** the folder copy for the computer; the claude.ai copy for the phone and the Claude app. Both show every run.
- **Update tasks:** "update Last Z Tasks" runs `git pull` in the folder, then republishes `dashboard/index.html` to the saved `dashboard_url` (pass it as `url` and omit `capabilities` so the page keeps its database rules). The run history is untouched.
- **Available tasks:** list the task skills in `.claude/skills/` (skip `last-z-setup` and `last-z-log-run`).
