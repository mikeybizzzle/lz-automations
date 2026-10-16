---
name: last-z-alliance-stats
description: Capture tracked alliance members' stats (HQ, power breakdown, kills) in Last Z on BlueStacks, log them to the alliance stats spreadsheet, and publish the alliance stats web page. Use when asked to track, log, capture or update alliance member stats.
---

# Last Z: Alliance Member Stats

Reads each tracked member's profile in Last Z: Survival Shooter (BlueStacks Air on the user's Mac), then:

1. adds a dated capture to `data/Last Z Alliance Stats.xlsx`,
2. exports the web page's data file and publishes the alliance page,
3. logs the run with `last-z-log-run`.

Everything lives in the workspace, usually `~/Last-Z-Tasks`. In a Claude Desktop or cloud session linked to the Mac, reach it with `device_bash` at `$HOME/mnt/<folder>/Last-Z-Tasks` (python3 and openpyxl are available there).

| Path in the workspace | What it is |
|---|---|
| `.claude/skills/last-z-alliance-stats/lz_stats.py` | The script that updates the spreadsheet and exports the page data |
| `data/Last Z Alliance Stats.xlsx` | The tracker. Git-ignored. |
| `data/alliance-runs/<date>.json` | One file per capture, kept as a backup. Git-ignored. |
| `alliance/index.html` | The page template |
| `alliance/data/alliance.js` | The page's data, written by the script. Git-ignored here. |
| `data/config.json` → `alliance_site_repo` | The GitHub repo the live page deploys from, e.g. `mikeybizzzle/rfc-member-intel` |

If `lz_stats.py` is missing (for example the skill was saved to a Claude account without the repo), clone `https://github.com/mikeybizzzle/lz-automations` and take it from this folder.

## Workbook tabs

- **Member Stats**: one 8-row block per player (HQ Level, Total Power, Kills, Structure, Tech, Hero, Mod Vehicle, Troop Power). One Number/Delta column pair per capture date. Rows 1-2 and columns A-B are frozen.
- **Member Reference**: Player Name, Rank (R1-R4), Active Member (Active/Inactive), Track Status (Yes/No). The user edits this tab. Only players with **Active + Yes** get captured.
- **Summary**: rebuilt on every run. For each stat except Troop Power, three tables ranked by % change: all time (since the first capture), since the previous capture, and the last 30 days. A watchlist at the top flags any stat (HQ and Troop excluded) that grew +0.1% or less in 7 days or +0.5% or less in 30 days.

## 1. Connect

- Read the computer-use skill first.
- Resolve and request access to **BlueStacks** (`com.now.gg.BlueStacks`).
- Use the background `computer_app_*` tools only (`computer_app_screenshot`, `computer_app_click`, `computer_app_batch`, `computer_app_zoom`). Taps and swipes both work in the background. Don't switch to full-screen control.
- Swipe = `drag` with a `path` of 8-12 points. Wait = a few tiny `zoom` actions (region [0,0,10,10], scale 0.1).

## 2. Load the tracked list

```bash
cd "$WS" && python3 .claude/skills/last-z-alliance-stats/lz_stats.py "data/Last Z Alliance Stats.xlsx" --tracked
```

This prints the capture list (name + last known rank). Those are the only profiles to open, plus any new members (see 4). Note the time you start, for the run log.

## 3. Open the member list

Coordinates are for the 624x1084 window frame seen on 2026-10-16. Check them against a fresh screenshot. Work them out again if the window size changes.

| Step | Tap | Confirm |
|---|---|---|
| a. Alliance (from base) | (554, 825) | Alliance screen with Wars / Help / Techs tiles |
| b. Members tab | (284, 1036) | "Members" title, R5 leader card at top |
| c. Scroll to the headers | swipe DOWN: drag (296,500) -> (296,910) | R4 / R3 / R2 / R1 header bars visible |

**The Members screen opens scrolled to the bottom.** A swipe up does nothing there. Swipe down first to see the rank headers.

- Header bars (after step c, with only R1 open): R4 about (300, 495), R3 about (300, 542), R2 about (300, 608), R1 about (300, 663). Each shows a member count. Tapping a header toggles that panel open/closed.
- Work one panel at a time: open it, finish it, collapse it. Open only the ranks the tracked list needs, plus R1 and R2 to catch new members.
- R3 holds ~67 members. Swipe through it and look for names only.

## 4. Who to read

- **Tracked players** (Active + Yes): read every one.
- **New R1/R2 members**: a name in the R1 or R2 panel that isn't on Member Reference and doesn't contain "farm". Read them too. The script adds them as Active + Yes. Report them so the user can switch any to No.
- **Never** read names containing "farm" (any case). Ignore untracked or Inactive names.
- **Rank**: record the panel each player was found in. The script updates Rank.
- **Missing**: if a tracked player isn't in their rank's panel, check R1, R2, R3 and R4. Only if they're in none of them, put them in `missing`. The script sets them to Inactive. Never mark someone missing because a tap failed.

Before opening profiles, screenshot each panel and list the names to read, so you can tick them off.

## 5. Read each member

Cards sit in a 2-column grid. Avatar centers: left column x=108, right column x=338. Rows are ~85 px apart.

Per member, one `computer_app_batch`:

1. Tap the avatar. A popup appears with **Details** and **Private Chat**.
   - Usually BELOW the avatar: Details at (130, y+42) for the left column, (267, y+42) for the right.
   - For the bottom visible row it appears ABOVE: Details at (130, y-40) / (267, y-40).
   - If unsure, screenshot after the avatar tap.
2. Tap **Details**. Wait ~1.5 s (the profile fades in).
3. Zoom region [80,160,380,345]: read the name and HQ level (`Lv.29`).
4. Tap the **Power** number at (163, 322). Wait ~2 s.
5. Zoom region [95,300,500,670]: the Details panel shows Total Power, Kills (skull icon), Structure, Tech, Troop, Hero, Mod Vehicle Power, as full numbers.
6. Close: Details X (480, 280), then profile X (483, 117).

If the zoom looks faded, the panel is still animating. Zoom again before you read. If the profile doesn't open, the Details tap missed: screenshot and retry.

To reach lower rows, swipe UP (drag (296,950) -> (296,410)). At the bottom of the list, rows sit at about y = 510, 595, 680, 765, 850, 935.

Record full integers, not the rounded card values.

## 6. Check the numbers

For every player: Structure + Tech + Troop + Hero + Mod Vehicle must equal Total Power exactly. If not, re-open that profile and re-read.

Copy names exactly as shown, including symbols (`---Shopi---`) and non-Latin text. The tabs match players by exact name, so a typo makes a new player.

## 7. Log to the spreadsheet

Write `data/alliance-runs/<date>.json`:

```json
{"date": "YYYY-MM-DD",
 "players": [{"name": "Everywhere", "rank": "R2", "hq": 29, "total": 225947700, "kills": 2581006,
              "structure": 64577418, "tech": 16154843, "hero": 45016518, "mod": 7713521, "troop": 92485400}],
 "missing": []}
```

Then, in the workspace:

```bash
S=.claude/skills/last-z-alliance-stats/lz_stats.py; X="data/Last Z Alliance Stats.xlsx"
python3 $S "$X" data/alliance-runs/<date>.json      # logs Member Stats, updates Member Reference, rebuilds Summary
python3 $S "$X" --export alliance/data/alliance.js  # writes the page's data file
```

The script refuses a date that's already logged. If the user only edited Member Reference and wants the Summary and page refreshed, run `--summary`, then `--export`.

## 8. Publish the alliance page

The live page deploys from the repo in `data/config.json` → `alliance_site_repo`. Vercel republishes on every push to its `main` branch, about a minute later.

1. Stage `alliance/index.html` and `alliance/data/alliance.js` into the session's container (`device_stage_files`).
2. Attach the site repo with push access (`add_repo`, access `push`), clone it, copy both files in (`index.html`, `data/alliance.js`), commit `Alliance stats <date>`, and push to `main`.
3. Check the live page's data file shows the new date (WebFetch `<site url>/data/alliance.js`). The site URL is in `data/config.json` → `alliance_site_url`.

If the repo can't be reached, say the page wasn't updated and the spreadsheet was. The next run (or "publish the alliance page") pushes the latest export.

## 9. Log the run

Follow `last-z-log-run` with:

| Field | Value |
|---|---|
| `task` / `label` | `alliance-stats` / `Alliance Stats` |
| `requested` | Tracked members at the start |
| `completed` | Members captured and sum-checked |
| `status` | `complete`, or `partial` if any tracked member wasn't read |
| `issues` | Re-reads, missed taps, members marked Inactive |
| `notes` | New members added, rank changes, watchlist flags |

## 10. Report

- Captured vs. tracked count.
- New members added, rank changes, players marked Inactive (all printed by the script).
- Top 3 Total Power gainers by % since the previous capture, and anyone on the watchlist.
- Whether the live page updated.

Release the computer lock when you're done.
