"""Game rules independent of the graphical interface."""
import random
from dataclasses import dataclass
from typing import Any
from pacman.maze import Maze, Point


@dataclass
class Ghost:
    """Enemy position, home corner and revival timer."""

    position: Point
    home: Point
    revive: float = 0.0


class Game:
    """Manage level progression, movement, scoring and timers."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Start a new run."""
        self.config = config
        self.level = 0
        self.score = 0
        self.lives: int = config['lives']
        self.state = 'playing'
        self.invincible = self.freeze = self.fast = False
        self.direction = self.wanted = (0, 0)
        self.player_clock = self.ghost_clock = 0.0
        self.rng = random.Random()
        self.start_level()

    def start_level(self) -> None:
        """Use a fixed first seed and random subsequent seeds."""
        level = self.config['levels'][self.level]
        seed = (self.config['seed'] if self.level == 0
                else self.rng.randint(1, 2**31 - 1))
        self.maze = Maze(level['width'], level['height'], seed)
        self.player = self.maze.center
        self.ghosts = [Ghost(p, p) for p in self.maze.corners]
        self.power = 0.0
        self.grace = 2.0
        self.remaining = float(level['level_max_time'])
        self.pellets = self.maze.reachable - {self.player}
        self.super_pellets = set(self.maze.corners)
        self.pellets -= self.super_pellets
        self.direction = self.wanted = (0, 0)
        self.player_clock = self.ghost_clock = 0.0

    def next_level(self) -> None:
        """Preserve score and lives when advancing."""
        self.level += 1
        if self.level == len(self.config['levels']):
            self.state = 'won'
        else:
            self.start_level()

    def collide(self) -> None:
        """Resolve collisions and protect the player's respawn."""
        for ghost in self.ghosts:
            if ghost.revive > 0 or ghost.position != self.player:
                continue
            if self.power > 0:
                self.score += self.config['points_per_ghost']
                ghost.revive = float(self.config['ghost_respawn_seconds'])
            elif not self.invincible and self.grace <= 0:
                self.lives -= 1
                self.player = self.maze.center
                self.direction = self.wanted = (0, 0)
                self.grace = 2.0
                if self.lives <= 0:
                    self.state = 'lost'
                return

    def move_player(self) -> None:
        """Follow a buffered turn when a passage is available."""
        neighbors = self.maze.neighbors(self.player)
        x, y = self.player
        desired = (x + self.wanted[0], y + self.wanted[1])
        if desired in neighbors:
            self.direction = self.wanted
        target = (x + self.direction[0], y + self.direction[1])
        if target in neighbors:
            self.player = target
        if self.player in self.pellets:
            self.pellets.remove(self.player)
            self.score += self.config['points_per_pacgum']
        if self.player in self.super_pellets:
            self.super_pellets.remove(self.player)
            self.score += self.config['points_per_super_pacgum']
            self.power = float(self.config['power_seconds'])
        self.collide()
        if (self.state == 'playing' and not self.pellets
                and not self.super_pellets):
            self.next_level()

    def move_ghosts(self) -> None:
        """Chase by corridor distance or flee while edible."""
        distances = self.maze.distances(self.player)
        for ghost in self.ghosts:
            if ghost.revive > 0:
                continue
            options = self.maze.neighbors(ghost.position)
            self.rng.shuffle(options)
            if options:
                ghost.position = sorted(
                    options, key=lambda p: distances.get(p, 99999),
                    reverse=self.power > 0)[0]
        self.collide()

    def update(self, dt: float) -> None:
        """Advance active simulation time in bounded steps."""
        if self.state != 'playing':
            return
        dt = max(0.0, min(dt, 0.1))
        self.remaining = max(0.0, self.remaining - dt)
        self.power = max(0.0, self.power - dt)
        self.grace = max(0.0, self.grace - dt)
        for ghost in self.ghosts:
            if ghost.revive > 0:
                ghost.revive = max(0.0, ghost.revive - dt)
                if ghost.revive == 0:
                    ghost.position = ghost.home
        if self.remaining <= 0:
            self.state = 'lost'
            return
        self.player_clock += dt
        self.ghost_clock += dt
        speed = self.config['player_speed'] * (2 if self.fast else 1)
        if self.player_clock >= 1 / speed:
            self.player_clock %= 1 / speed
            self.move_player()
        if self.state != 'playing':
            return
        if self.ghost_clock >= 1 / self.config['ghost_speed']:
            self.ghost_clock %= 1 / self.config['ghost_speed']
            if not self.freeze:
                self.move_ghosts()
