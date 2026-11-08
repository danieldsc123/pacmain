"""Canvas-only desktop interface with keyboard and mouse navigation."""
from __future__ import annotations

import logging
import math
import time
import tkinter as tk
from pathlib import Path
from typing import Any, Callable
from pacman.model import Game
from pacman.scores import Scores

BG = '#080c19'
WHITE = '#edf3ff'
CYAN = '#55ddff'


class App:
    """Draw the game using basic shapes, text and window events."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Create the window, callbacks and persistent ranking."""
        self.config = config
        self.scores = Scores(Path(config['highscore_filename']))
        self.root = tk.Tk()
        self.root.title('PAC-MAN / 42 Arcade')
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=960, height=780,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.screen = 'menu'
        self.game: Game | None = None
        self.name = ''
        self.message = ''
        self.cheats = False
        self.buttons: list[tuple[int, int, Callable[[], None]]] = []
        self.root.bind('<KeyPress>', self.key)
        self.canvas.bind('<Button-1>', self.click)
        self.root.protocol('WM_DELETE_WINDOW', self.root.destroy)
        self.root.report_callback_exception = self.callback_error
        self.previous = time.monotonic()
        self.tick()

    def callback_error(self, kind: Any, error: Any, trace: Any) -> None:
        """Recover from callback failures without a Python traceback."""
        logging.error('Game error: %s', error)
        self.message = f'Game error: {error}'
        self.screen = 'menu'

    def text(self, x: float, y: float, text: str,
             size: int = 18, color: str = WHITE) -> None:
        """Draw a text label."""
        self.canvas.create_text(x, y, text=text, fill=color,
                                font=('Courier', size, 'bold'))

    def button(self, y: int, title: str,
               action: Callable[[], None]) -> None:
        """Draw a selectable menu row."""
        self.canvas.create_rectangle(260, y - 23, 700, y + 23,
                                     fill='#14233c', outline='#284975')
        self.text(480, y, title)
        self.buttons.append((y - 23, y + 23, action))

    def show(self, screen: str) -> None:
        """Change the visible screen."""
        self.screen = screen

    def start(self) -> None:
        """Generate a new game; surface generator failures in the menu."""
        try:
            self.game = Game(self.config)
            self.screen = 'playing'
            self.message = ''
        except Exception as exc:
            logging.error('Maze generator failed: %s', exc)
            self.message = f'Maze generation failed: {exc}'
            self.screen = 'menu'

    def click(self, event: tk.Event[Any]) -> None:
        """Dispatch clicks on visible menu rows."""
        if 260 <= event.x <= 700:
            for low, high, action in self.buttons:
                if low <= event.y <= high:
                    action()
                    break

    def save(self) -> None:
        """Save a finished run and return to the menu."""
        if self.game:
            ok = self.scores.save(self.name, self.game.score)
            self.message = 'Score saved!' if ok else 'Could not save score.'
        self.screen = 'menu'

    def key(self, event: tk.Event[Any]) -> None:
        """Handle menu, movement, pause, evaluation and name input."""
        key = event.keysym.lower()
        game = self.game
        if self.screen == 'end':
            if key == 'return':
                self.save()
            elif key == 'backspace':
                self.name = self.name[:-1]
            elif (event.char and len(self.name) < 10
                  and (event.char.isalnum() or event.char == ' ')):
                self.name += event.char
            return
        if self.screen == 'menu':
            if key in ('return', '1'):
                self.start()
            elif key == '2':
                self.show('scores')
            elif key == '3':
                self.show('help')
            elif key in ('4', 'escape'):
                self.root.destroy()
            return
        if self.screen in ('scores', 'help'):
            if key in ('escape', 'return'):
                self.show('menu')
            return
        if key in ('p', 'escape'):
            self.screen = ('paused' if self.screen == 'playing'
                           else 'playing')
            return
        if self.screen == 'paused':
            if key == 'm':
                self.show('menu')
            return
        if game is None:
            return
        directions = {'up': (0, -1), 'w': (0, -1),
                      'down': (0, 1), 's': (0, 1),
                      'left': (-1, 0), 'a': (-1, 0),
                      'right': (1, 0), 'd': (1, 0)}
        if key in directions:
            game.wanted = directions[key]
        elif key == 'f1':
            self.cheats = not self.cheats
        elif self.cheats:
            if key == 'i':
                game.invincible = not game.invincible
            elif key == 'f':
                game.freeze = not game.freeze
            elif key == 'b':
                game.fast = not game.fast
            elif key == 'l':
                game.lives += 1
            elif key == 'n':
                game.next_level()
            elif key == 'o':
                game.power = float(self.config['power_seconds'])

    def draw_maze(self, game: Game) -> None:
        """Draw wall masks, collectibles and character primitives."""
        maze = game.maze
        cell = min(880 / maze.width, 550 / maze.height)
        ox = (960 - maze.width * cell) / 2
        oy = 125.0
        for y, row in enumerate(maze.cells):
            for x, mask in enumerate(row):
                left, top = ox + x * cell, oy + y * cell
                for bit, coords in (
                    (1, (left, top, left + cell, top)),
                    (2, (left + cell, top, left + cell, top + cell)),
                    (4, (left, top + cell, left + cell, top + cell)),
                    (8, (left, top, left, top + cell))
                ):
                    if mask & bit:
                        self.canvas.create_line(*coords, fill='#3465ee',
                                                width=2)
        for points, radius, color in ((game.pellets, 2.0, '#ffe1b0'),
                                      (game.super_pellets, 6.0, CYAN)):
            for x, y in points:
                cx, cy = ox + (x + .5) * cell, oy + (y + .5) * cell
                self.canvas.create_oval(cx - radius, cy - radius,
                                        cx + radius, cy + radius,
                                        fill=color, outline='')
        x, y = game.player
        cx, cy = ox + (x + .5) * cell, oy + (y + .5) * cell
        radius = cell * .35
        color = '#ffffff' if game.grace > 0 else '#ffda35'
        angle = {(1, 0): 0, (-1, 0): 180,
                 (0, -1): 90, (0, 1): 270}.get(game.direction, 0)
        self.canvas.create_arc(cx - radius, cy - radius,
                               cx + radius, cy + radius,
                               start=angle + 25, extent=310,
                               fill=color, outline='')
        for ghost, color in zip(game.ghosts,
                                ('#ff577b', '#ffacd9', '#5fe5ef', '#ffad60')):
            if ghost.revive > 0:
                continue
            gx = ox + (ghost.position[0] + .5) * cell
            gy = oy + (ghost.position[1] + .5) * cell
            fill = '#476aff' if game.power > 0 else color
            self.canvas.create_oval(gx - radius, gy - radius,
                                    gx + radius, gy + radius,
                                    fill=fill, outline='')
            for dx in (-.12, .12):
                ex = gx + cell * dx
                self.canvas.create_oval(ex - 2, gy - 3, ex + 2, gy + 1,
                                        fill=WHITE, outline='')

    def draw(self) -> None:
        """Render the current screen and its active controls."""
        self.canvas.delete('all')
        self.buttons.clear()
        self.text(480, 48, 'PAC-MAN', 38, '#ffda35')
        game = self.game
        if self.screen in ('playing', 'paused') and game:
            self.text(480, 96,
                      f'SCORE {game.score:06}    LIVES {game.lives}    '
                      f'LEVEL {game.level + 1}    TIME {math.ceil(game.remaining)}',
                      16)
            self.draw_maze(game)
            self.text(480, 710, 'WASD / Arrows   P Pause   F1 Cheats', 14)
            flags = [label for enabled, label in
                     ((game.invincible, 'INVINCIBLE'), (game.freeze, 'FROZEN'),
                      (game.fast, 'FAST'), (game.power > 0, 'POWER')) if enabled]
            self.text(480, 742, ' / '.join(flags), 12, CYAN)
            if self.cheats:
                self.text(480, 765, 'I God  F Freeze  B Speed  L Life  N Skip  O Power',
                          12, CYAN)
            if self.screen == 'paused':
                self.canvas.create_rectangle(220, 260, 740, 500,
                                             fill=BG, outline=CYAN)
                self.text(480, 300, 'PAUSED', 26)
                self.button(370, 'Resume [P]', lambda: self.show('playing'))
                self.button(440, 'Main menu [M]', lambda: self.show('menu'))
        elif self.screen == 'menu':
            self.text(480, 110, '42 ARCADE / TEN MAZES / ONE CHALLENGE', 14, CYAN)
            for y, title, action in (
                (230, '1  Start game', self.start),
                (300, '2  Highscores', lambda: self.show('scores')),
                (370, '3  Instructions', lambda: self.show('help')),
                (440, '4  Exit', self.root.destroy)
            ):
                self.button(y, title, action)
            self.text(480, 510, 'TOP SCORES', 18, CYAN)
            for i, (name, score) in enumerate(self.scores.entries[:3]):
                self.text(480, 550 + i * 32, f'{name:10}  {score:08}', 16)
            self.text(480, 710, self.message[:85], 12, CYAN)
        elif self.screen == 'scores':
            self.text(480, 120, 'HIGH SCORES / TOP 10', 22, CYAN)
            for i, (name, score) in enumerate(self.scores.entries):
                self.text(480, 175 + i * 43,
                          f'{i + 1:2}. {name:10}   {score:08}', 18)
            self.button(690, 'Back [Enter]', lambda: self.show('menu'))
        elif self.screen == 'help':
            lines = ['WASD / Arrows: move through corridors',
                     'Eat every dot and power pellet to advance.',
                     'Power pellets let you eat fleeing ghosts.',
                     'Four ghosts chase you. You start with 3 lives.',
                     'Losing a life respawns you with 2s protection.',
                     'Finish all levels to win. Timeout ends the run.',
                     'P / Escape: pause. M: menu while paused.',
                     'F1 toggles evaluation controls:',
                     'I invincibility / F freeze / B double speed',
                     'L extra life / N next level / O power',
                     'Enter your name after a win or loss.']
            for i, line in enumerate(lines):
                self.text(480, 160 + i * 41, line, 14)
            self.button(690, 'Back [Enter]', lambda: self.show('menu'))
        elif self.screen == 'end' and game:
            self.text(480, 220, 'VICTORY!' if game.state == 'won'
                      else 'GAME OVER', 36, CYAN)
            self.text(480, 310, f'FINAL SCORE {game.score}', 24)
            self.text(480, 400, 'Your name (10 letters / digits / spaces)', 16)
            self.text(480, 455, self.name + '_', 28, '#ffda35')
            self.button(550, 'Save score [Enter]', self.save)

    def tick(self) -> None:
        """Schedule frames and handle failures without killing the window."""
        now = time.monotonic()
        dt, self.previous = now - self.previous, now
        try:
            if self.screen == 'playing' and self.game:
                self.game.update(dt)
                if self.game.state in ('won', 'lost'):
                    self.name = ''
                    self.screen = 'end'
            self.draw()
        except Exception as exc:
            self.callback_error(type(exc), exc, None)
        self.root.after(16, self.tick)

    def run(self) -> None:
        """Run the native window event loop."""
        self.root.mainloop()
