# Implementation plan and status

Date: 2026-11-07. Participants: **danda-si** and **jaalves-**. Responsibility assignments remain
to be documented by the team.

| Work item | Dependency | Status |
| --- | --- | --- |
| Inspect subject and assigned wheel | Supplied inputs | Complete |
| Config parsing, defaults, maze adapter | Requirements/API analysis | Complete |
| Rules, timers, ghosts, progression | Maze adapter | Complete |
| Menu, gameplay, pause, result and ranking screens | Model | Implemented |
| Automated checks and native packaging | Implementation | See VALIDATION.md |
| Desktop playthrough and clean-machine acceptance | Desktop access | Pending human acceptance |
| Free restricted/unlisted platform delivery | Account and upload | Pending |
| Team identities | danda-si and jaalves- | Complete |
| Responsibility assignments and peer review | Both participants | Pending |

This is an implementation record, not a fabricated historical schedule. Suggested
remaining sequence: desktop playthrough, peer code review, clean-machine install,
platform upload, then record the delivery link and final acceptance evidence.

## Decisions and risks

- Keep the assigned wheel byte-for-byte unchanged. Reinstallation must not require
  generator edits. Adapter consumes wall masks and preserves isolated ornament.
- Separate rules from rendering so gameplay can be tested without a display.
- Use a local atomic JSON ranking: simple and inspectable, without a server.
- Timeout loses the run, avoiding repeated timer or maze resets.
- Larger maps may have a less readable fixed window; dimensions are bounded.
- File permission errors must warn without ending gameplay.
- Native builds are OS-specific and require target-machine testing.
- Tkinter must exist on source installations; packaged distributions bundle Tk.
- Backend uses primitives analogous to MLX; local evaluator interpretation needs
  confirmation if they require an exact binding.

## Acceptance plan

Automated: reproducible first seed, reciprocal movement, reachable spawns,
regular-dot scoring, damage and protection, power/ghost scoring and revival,
pause timing, ten-level victory, timeout loss, config comments/invalid values,
corrupt score storage, name filtering, sorting and persisted top ten.

Manual: open menu; exercise every keyboard and mouse option; play with all
movement keys; verify blocked walls, HUD, power pellet visuals, pause and resume;
lose all lives; use cheats to finish all levels; submit names after both results;
restart and verify ranking; edit config during defense; reinstall assigned wheel;
run extracted package on a fresh target system. Record observed outcomes and any
bugs in VALIDATION.md. Do not mark manual checks passed without performing them.
