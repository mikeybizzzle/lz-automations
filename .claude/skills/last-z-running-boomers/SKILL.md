---
name: last-z-running-boomers
description: Run a requested number of Stegosaurus (Boomer) rallies in Last Z: Survival Shooter on BlueStacks via computer use, then log the run. Use when asked to run boomers or rally Stegosauruses.
---

# Last Z: Running Boomers

Boomers = **Stegosaurus**. Not Velociraptor. The game runs in BlueStacks Air on the user's Mac.

## 1. Connect

- Read the computer-use skill first.
- Resolve and request access to **BlueStacks** (`com.now.gg.BlueStacks`).
- Use the background `computer_app_*` tools (`computer_app_screenshot`, `computer_app_click`, `computer_app_batch`). They operate the game directly. You don't need a native-click script or full-screen control.
- Note the start time for the log.

## 2. Ask only what's missing (one AskUserQuestion call)

- Stegosaurus level.
- Is Auto-Team off? If it's on, tell the user to tap their rally square and turn it off, then wait for them.
- Total rallies. Put the fuel cost in each option (16 fuel x count).

Ask everything up front. Once the loop starts the user may walk away, so don't stop to ask anything the skill already answers.

Don't ask how many formations they have. The game picks the first idle one, and the sidebar shows n/4.
Don't reuse answers from an earlier session.

## 3. Fuel check (do it yourself)

The Team Up dialog shows current fuel at the top right (e.g. `256/150`; it can be over the cap). Read it on the first Team Up and record it as fuel before. If fuel is less than 16 x the remaining rallies, tell the user the shortfall before you continue.

## 4. Rally loop

These coordinates are for the 624x1084 window frame seen on 2026-10-16. Check them against a fresh screenshot every time, and work them out again if the window size changes.

| Step | Tap | Confirm before the next step |
|---|---|---|
| a. World (only from base) | (540, 1045) | World map is showing |
| b. Magnifier | (30, 880) | Search panel is open: Velociraptor / Stegosaurus / Lumberyard row and a Search button |
| c. Stegosaurus (first loop only) | (275, 720) | Stegosaurus is highlighted |
| d. Level | minus (138, 972) / plus (450, 972) | Label shows the requested level. Selecting Stegosaurus can jump to its max (it showed Lv.50), so always check. The level stays set for the rest of the session. |
| e. Search | (295, 1032) | Popup reads "Lv.NN Stegosaurus". The map pans for about 2-3 s first. |
| f. Team Up | about (290, 810), under the popup | Formation dialog with a March button that costs 16 fuel |
| g. March | (308, 760) | Red ring on the target, a new 1m countdown on a sidebar portrait, and n/4 goes up by one |

Count a launch only after you see the step g confirmation. Stop as soon as the verified count matches the target.

**Batching.** It's safe to run one `computer_app_batch` per step: click, short wait, then a screenshot at scale 0.5. For a wait, add a few tiny `zoom` actions. Never chain the magnifier tap straight into Search without seeing the panel. Right after a launch the map is still moving, so the magnifier tap can get swallowed and the Search tap lands on the chat bar instead. If Chat opens, tap the back arrow at (40, 1028).

## 5. All formations busy

When every formation is out, tapping **Team Up** (not March) shows "The number of march queues has reached its limit." The target popup stays open. Read the shortest sidebar timer, wait that long plus a few seconds, then tap Team Up again. Don't recall troops or use speedups. With the 1m rally timer, a formation comes back about 1.5-2 min after launch, so with 3 formations this rarely blocks.

## 6. Out of fuel (not tested yet)

If **Fuel Replenish** shows where March should be:

1. Open it and look at the dialog.
2. Drag the bar to max.
3. Confirm it uses a fuel reserve, not diamonds or a purchase.
4. Finish the refill and retry March.

If it needs diamonds or money, stop. Log the run as `partial` and say why in the notification. A refill doesn't count as a launch.

## 7. Report and log

Give the user a short report:

- Requested count vs. verified launches, plus which formation went out each time.
- Fuel before and after. Read fuel after from the last Team Up dialog, minus 16 for that final launch.
- Anything unusual: the level reset, misclicks, errors, "Neck and Neck" or "Insufficient Virus Resistance" warnings. Mention these, but don't stop for them.
- These don't count as launches: Today's Claims (x/15), Boomer Spoils toasts, battle results.

Then follow the **last-z-log-run** skill with:

- `task`: `running-boomers`
- `label`: `Running Boomers`
- `settings`: `{"level": <level>}`
- `requested` / `completed`: rallies asked for / verified
- `resources`: `{"fuel": {"before": <n>, "after": <n>}}`

Release the computer lock when you're done.
