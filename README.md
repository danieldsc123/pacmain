*This project has been created as part of the 42 curriculum by danda-si, jaalves-.*

# Pac-Man

## Description

A Python 3.10+ desktop arcade game with ten generated mazes, four chasing
ghosts, power pellets, persistent scores and evaluation controls.

Team: **danda-si** and **jaalves-**.

## Instructions

Linux requires Python with Tk support (distribution package `python3-tk`).
Windows/macOS Python installers commonly include Tk. A graphical desktop is
required. No network is used by the game.

```sh
python3 -m venv .venv
. .venv/bin/activate
make install
python3 pac-man.py config.json
```

Pass exactly one argument. Invalid or absent configuration files produce warnings
and safe defaults. Incorrect argument count prints usage. `make run`, `make debug`,
`make lint`, `make lint-strict`, `make test`, and `make clean` are also available.
Set `CONFIG=other.json` for run/debug. Dependencies include the original supplied
wheel, development checkers and the packaging tool.

Controls: arrow keys or WASD move; P/Escape pauses; M returns to menu when paused.
Mouse selects menu rows; Enter starts from the main menu or saves a finished run.
F1 toggles cheat controls; I toggles invincibility; F freezes ghost movement;
B toggles double speed; L adds a life; N skips a level; O enables power.
Turning off the cheat controls hides their bindings; enabled effects are shown
in the HUD and remain until toggled or a new run starts.

You must eat both regular and power pellets to clear a level. Timeout ends the
run. Damage respawns the player at the nearest reachable center with two seconds
of protection. Pause freezes all gameplay timers. Eaten ghosts revive at their
corners after five seconds by default. Scores never decrease.

## Configuration

Configuration is JSON with optional whole lines beginning with `#` (leading
whitespace is accepted). Unknown keys are ignored. Invalid settings use defaults
and log warnings. Boolean values are not accepted as integers.

| Key | Default | Allowed values |
| --- | --- | --- |
| highscore_filename | highscores.json | Nonempty filename, relative to config directory |
| lives | 3 | Integer 1–20 |
| seed | 42 | Integer 1–3600; first level only |
| points_per_pacgum | 10 | Integer 0–999999 |
| points_per_super_pacgum | 50 | Integer 0–999999 |
| points_per_ghost | 200 | Integer 0–999999 |
| level_max_time | 90 | Integer seconds 1–3600 |
| power_seconds | 8 | Integer seconds 1–3600 |
| ghost_respawn_seconds | 5 | Integer seconds 1–3600 |
| player_speed | 7 | Integer cells/second 1–20 |
| ghost_speed | 4 | Integer cells/second 1–20 |
| levels | Ten empty objects | Array of level objects; padded to 10, capped at 100 |

Each level supports `width` (default 19, range 9–35), `height` (default 15,
range 9–25), and `level_max_time` (default global limit). `level` is accepted as
an alias for `levels`. Most reachable cells contain a dot; the spawn cell is
empty and the four corners contain power pellets instead. Collectible count is
derived from the generated corridors rather than an independent `pacgum` count.

## Highscore

The JSON table stores `{ "name": "Player", "score": 123 }` records. At startup,
records are validated, sorted descending and limited to ten. Names accept at most
ten Unicode alphanumeric characters or spaces; empty names become Player.
Scores must be nonnegative integers (booleans rejected). Corrupt or missing
storage starts an empty table. Saving uses a temporary file in the same directory
and atomic replacement to reduce partial writes. File errors are logged and
shown in the menu; the in-memory table stays usable. JSON keeps this small local
ranking readable and requires no database server. Win and loss both request a name.

## Maze Generation

`vendor/mazegenerator-2.1.0-py3-none-any.whl` is copied unchanged from the supplied
ZIP. Install a replacement assigned wheel through pip during evaluation; no
vendored generator source or substitute algorithm is used.

The adapter calls `MazeGenerator(size=(width, height), perfect=False, seed=seed)`
and consumes `.maze`, whose N/E/S/W wall bits are 1/2/4/8. The adapter validates
dimensions and wall masks, checks reciprocal openings, and performs breadth-first
search over existing passages. This search does not carve or generate walls.
The generator's isolated 42 ornament is preserved. Spawn positions are selected
from reachable cells, choosing the closest available center/corners. First-level
seed is fixed; subsequent levels use random positive seeds. Generator errors
return the player to the menu with a readable message; no fallback generator exists.

## Implementation

Simulation uses explicit elapsed-time deltas capped at 100 ms to avoid large
jumps after window stalls. Player turns are buffered until the corridor opens.
Ghosts choose shortest-path neighbors when chasing, and farthest-path neighbors
when frightened; ties are shuffled. Collision checks happen after player movement
and after ghost movement, so corridor swaps cannot silently pass through a ghost.
All four ghosts share this chase strategy; distinct original arcade personalities
are not required. A monotonic clock drives Tk's scheduled frame callback.

The graphical backend is Tkinter Canvas, using basic window creation, key/mouse
hooks, scheduled updates, text and shape drawing. It does not use collision,
pathfinding, physics or sprite engine facilities. Shapes can be rasterized into
MLX image pixels; text maps to string output, callbacks to hooks, and scheduled
frames to loop hooks. Confirm this primitive-based backend interpretation with
your evaluator if a specific MLX binding is mandated locally.

## General Software Architecture

- `pac-man.py`: command-line validation and startup error boundary.
- `pacman/config.py`: validated settings and defaults.
- `pacman/maze.py`: external generator adapter and passage graph.
- `pacman/model.py`: Game and Ghost state, scoring, movement and progression.
- `pacman/scores.py`: validation and atomic top-ten persistence.
- `pacman/ui.py`: App, rendering, menu states and input routing.
- `package.py`: native executable and ZIP build.

The UI owns a Game and Scores instance. Game owns Maze and four Ghost objects.
The model has no Tk dependency, allowing headless acceptance tests.

## Packaging and deployment

```sh
make package
cd dist/pac-man
./pac-man config.json
```

`dist/pac-man-native.zip` includes a native executable, editable configuration,
README and brief controls. Build separately on each target OS; this is not a
cross-compilation script. Run the executable from its extracted directory.
Write permission there is needed for the default ranking file. The command-line
configuration argument remains required for the packaged executable.

Public platform deployment remains a manual delivery step: create a free
restricted/unlisted downloadable-game page on Itch.io (or an equivalent platform),
upload the native ZIP, select its actual target OS, and document the private
review link in `project_management/DELIVERY.md`. No upload or publication has
been performed by this implementation. Verify the downloaded build on a clean
machine before presenting it for evaluation.

## Project Management

See [project_management](project_management/PLAN.md) for scope, decisions, risk,
acceptance checks and honest delivery status. Historical planning and responsibility assignments
must be completed by the actual participants; generated documents do
not claim work or meetings that did not occur.

## Resources

- Python documentation: `json`, `tkinter`, `collections.deque`, `unittest`, `tempfile`.
- The supplied Pacman subject version 1.5 and assigned MazeGenerator wheel.
- PyInstaller manual: native executable bundling and platform-specific builds.
- Classic Pac-Man rules and breadth-first search on unweighted graphs.

AI was used to read the supplied requirements, implement the config adapter,
maze integration, game model, interface, ranking, build tooling, acceptance tests
and documentation. Review and understand all generated code before defense;
peer review and responsibility assignments remain the team's responsibility.
