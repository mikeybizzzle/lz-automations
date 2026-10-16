# LZ Automations

Claude skills that automate repeatable tasks in **Last Z: Survival Shooter**. The game runs in BlueStacks Air on macOS, and Claude drives it with computer use.

## Skills

| Skill | What it does | Status |
|---|---|---|
| [last-z-running-boomers](skills/last-z-running-boomers/SKILL.md) | Runs a set number of Stegosaurus (Boomer) rallies. It checks fuel, waits when every formation is busy, and verifies each launch. | Tested 2026-10-16: 10/10 level-49 rallies |

## Layout

```
skills/
  <skill-name>/
    SKILL.md      # instructions Claude follows
```

Each skill folder holds a `SKILL.md` with `name` and `description` frontmatter. Scripts or reference files for a skill go in the same folder.

## Adding a new task

1. Walk Claude through the task once in the game.
2. Have Claude write it up as `skills/<task-name>/SKILL.md`. Include:
   - the setup questions to ask
   - each tap, with what to confirm before the next one
   - how to handle errors
   - what goes in the end report
3. Test it with a live run, fix what the game did differently, then add a row to the table above.

## Notes

- Tap positions are recorded for the BlueStacks window size used during testing. Each skill tells Claude to check them against a fresh screenshot before tapping.
- These skills don't spend diamonds or real money. Anything that would needs Mike's approval first.
