# Itch.io page preparation

## Suggested page text

Title: Pac-Man — 42 Project
Short description: A ten-level Python arcade game by danda-si and jaalves-.

A Pac-Man recreation created as part of the 42 curriculum by danda-si and
jaalves-. Explore ten generated mazes, collect every pellet, avoid four ghosts,
and use power pellets to turn the chase around. Includes a local top-ten ranking,
pause menu and evaluation cheats.

Linux native download. Extract the ZIP, open a terminal in the extracted
`pac-man` directory and run:

```sh
chmod +x pac-man
./pac-man config.json
```

Controls: WASD or arrows to move; P/Escape to pause; M returns to the main menu
while paused. F1 enables evaluation controls: I invincibility, F freeze ghosts,
B double speed, L extra life, N skip level, O power. Enter saves your name after
a win or loss. See the bundled README for editable configuration options.

## Publication checklist

- Create a downloadable game at https://itch.io/game/new.
- Set pricing to No payments.
- Upload `dist/pac-man-native.zip` and select Linux as the supported platform.
- Use Restricted visibility with password access for reviewers, or Public with
  Unlisted in search & browse enabled. Draft is not the delivery state.
- Add the description and launch command above.
- Save, download the uploaded ZIP and test gameplay on a graphical Linux desktop.
- Record the actual URL and acceptance results in DELIVERY.md and VALIDATION.md.
- Share reviewer passwords separately; do not commit credentials.

Official references:
https://itch.io/docs/creators/access-control
https://itch.io/docs/creators/pricing
