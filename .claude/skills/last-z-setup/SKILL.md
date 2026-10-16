---
name: last-z-setup
description: Set up, update or check the Last Z Tasks workspace (task skills, run log and the claude.ai dashboard) on the user's Mac. Use when asked to set up or update Last Z, install Last Z Tasks, or when a Last Z task can't find its workspace.
---

# Set up Last Z Tasks

Goal: the user ends up with a `Last-Z-Tasks` folder on their Mac that holds the task skills and the run log (`data/runs.json`), plus their own private dashboard on claude.ai that they open in the Claude app on their computer or phone. Safe to run again: it never overwrites existing run data or creates a second dashboard.

Repo: `https://github.com/mikeybizzzle/lz-automations`

## 1. Get the workspace onto the Mac

Check which situation you're in:

**A. You're already inside a copy.** The current or connected folder contains `CLAUDE.md` and `.claude/skills/last-z-log-run/`. Skip to step 2.

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

If `data/runs.json` doesn't exist, create it with:

```json
{
  "runs": []
}
```

If it exists, leave it as is and report how many runs it holds.

**Older workspaces:** if there's a `data/runs.js` from an earlier version (one `LZ_RUNS.push({...});` line per run), move its runs into `data/runs.json` (same objects, same order, skipping any `id` already there), check the run count matches, then delete `data/runs.js`.

`data/` is git-ignored, so updating the workspace with `git pull` never touches the log.

## 3. Check the game connection

- Resolve and request computer-use access to **BlueStacks** (`com.now.gg.BlueStacks`). If computer use isn't available, tell the user it needs the Claude desktop app open on the Mac with computer use turned on (Settings → This computer → Computer use).
- Take one screenshot to confirm the game is visible. Don't tap anything.

## 4. Create the claude.ai dashboard

The template is **`dashboard/index.html`** in the workspace. Each user publishes their own private copy to claude.ai. It reads runs from the page's own database, which **last-z-log-run** keeps identical to `data/runs.json`. The file isn't meant to be opened locally.

1. **Already set up?** If `data/config.json` has a `dashboard_url`, `read` it with the Artifact tool to confirm it still exists, then go straight to **Sync** below. If it's gone, continue.
2. **Found an existing one?** `list` the user's artifacts and look for one titled "Last Z Tasks". If there is one, ask whether to use it. If yes, skip publishing and go to **Save the link**.
3. **Publish** `dashboard/index.html` with the Artifact tool:
   - `capabilities`: `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}}` (anyone the user shares it with can read; only the user writes)
   - `icon`: `chart`
   - `description`: `Live log of my automated Last Z runs, with every run's details.`

   The Artifact tool publishes from a file in this session's own working or scratchpad folder. If the workspace is only reachable on the Mac (a cloud session), stage `dashboard/index.html` with `device_stage_files`, copy it into the scratchpad, and publish that copy.
4. **Save the link** to `data/config.json` as `{"dashboard_url": "<url>"}`, keeping any other keys already there. `data/` is git-ignored, so the link stays private.
5. **Sync** existing runs: follow step 3 of **last-z-log-run**.
6. **Show it:** open it in the chat with the Artifact tool (`action: "open"`). Offer once to pin it to the user's sidebar. It's private until they share it from the page's Share menu.

If this session has no Artifact tool (Claude Code in a terminal, for example), skip this step and tell the user to run "set up Last Z" once from a Claude Desktop chat with the folder connected to create the dashboard.

## 5. Tell the user how to use it

Keep it short:

- **Run a task:** for example, "run 10 boomers." Claude asks its setup questions first, then runs the task without needing them.
- **Step away safely:** keep the Mac awake and unlocked, and keep the Claude desktop app and BlueStacks open. Computer use can't work while the screen is locked or the Mac is asleep. Turning off auto-lock and sleep in System Settings for the duration of a run is enough.
- **Phone alerts:** when a task ends, Claude sends a one-line summary if the session has notifications. In Claude Code that's a desktop notification, which also reaches the phone when Remote Control is on. Without notifications, the summary waits in the chat.
- **Dashboard:** it opens in the chat after every run. Any time, say "open my Last Z dashboard". It's also in their artifacts in the Claude app on the phone.
- **Update tasks:** "update Last Z Tasks" runs `git pull` in the folder, then republishes `dashboard/index.html` to the saved `dashboard_url` (pass it as `url` and omit `capabilities` so the page keeps its database rules). The run history is untouched.
- **Available tasks:** list the task skills in `.claude/skills/` (skip `last-z-setup` and `last-z-log-run`).
