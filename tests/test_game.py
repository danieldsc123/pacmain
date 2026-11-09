"""Verifica a aceitação das regras, da configuração e do armazenamento."""
import json
import tempfile
import unittest
from pathlib import Path
from pacman.config import load
from pacman.model import Game
from pacman.scores import Scores


class Acceptance(unittest.TestCase):
    """Testa o gerador externo real e as regras determinísticas do jogo."""

    def setUp(self) -> None:
        """Carrega a configuração fornecida com o projeto."""
        self.config = load(Path('config.json'))
        self.game = Game(self.config)

    def test_maze(self) -> None:
        """Verifica sementes reproduzíveis, passagens recíprocas e itens acessíveis."""
        other = Game(self.config)
        self.assertEqual(self.game.maze.cells, other.maze.cells)
        maze = self.game.maze
        self.assertEqual(len(self.game.ghosts), 4)
        self.assertEqual(len(self.game.super_pellets), 4)
        self.assertIn(maze.center, maze.reachable)
        for point in maze.reachable:
            for neighbor in maze.neighbors(point):
                self.assertIn(point, maze.neighbors(neighbor))

    def test_collision(self) -> None:
        """Verifica dano, proteção ao reaparecer, pontos de poder e renascimento."""
        game = self.game
        game.grace = 0
        game.ghosts[0].position = game.player
        game.collide()
        self.assertEqual(game.lives, 2)
        game.collide()
        self.assertEqual(game.lives, 2)
        game.power = 8
        game.collide()
        self.assertEqual(game.score, 200)
        self.assertEqual(game.ghosts[0].revive, 5)
        for _ in range(51):
            game.update(.1)
        self.assertEqual(game.ghosts[0].revive, 0)

    def test_progression_pause_timeout(self) -> None:
        """Verifica dez níveis, pontos, vidas, pausa e derrota por tempo esgotado."""
        game = self.game
        game.score = 123
        game.lives = 2
        game.state = 'paused'
        remaining = game.remaining
        game.update(.1)
        self.assertEqual(game.remaining, remaining)
        game.state = 'playing'
        for _ in range(10):
            game.next_level()
        self.assertEqual((game.state, game.score, game.lives), ('won', 123, 2))
        other = Game(self.config)
        other.remaining = .01
        other.update(.1)
        self.assertEqual(other.state, 'lost')

    def test_movement_and_pellet(self) -> None:
        """Verifica o movimento e a pontuação única das pastilhas comuns."""
        game = self.game
        game.ghosts.clear()
        target = next(p for p in game.maze.neighbors(game.player)
                      if p in game.pellets)
        game.wanted = (target[0] - game.player[0],
                       target[1] - game.player[1])
        game.move_player()
        self.assertEqual(game.player, target)
        self.assertEqual(game.score, 10)
        self.assertNotIn(target, game.pellets)

    def test_power_flee_and_walls(self) -> None:
        """Verifica superpastilhas, fuga dos fantasmas e bloqueio pelas paredes."""
        game = self.game
        game.ghosts.clear()
        game.player = next(iter(game.super_pellets))
        game.move_player()
        self.assertEqual(game.score, 50)
        self.assertEqual(game.power, 8)
        game.move_player()
        self.assertEqual(game.score, 50)
        game.player = (0, 0)
        game.wanted = game.direction = (-1, 0)
        game.move_player()
        self.assertEqual(game.player, (0, 0))
        other = Game(self.config)
        other.power = 8
        distances = other.maze.distances(other.player)
        expected = [max(distances[p] for p in
                        other.maze.neighbors(g.position))
                    for g in other.ghosts]
        other.move_ghosts()
        self.assertEqual([distances[g.position] for g in other.ghosts],
                         expected)

    def test_config_and_scores(self) -> None:
        """Verifica comentários, tipos inválidos, registros corrompidos e ranking."""
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'test.json'
            config.write_text('# comment\n' + json.dumps({
                'lives': True, 'levels': [{'width': -1}], 'unknown': 7}))
            result = load(config)
            self.assertEqual(result['lives'], 3)
            self.assertEqual(len(result['levels']), 10)
            self.assertEqual(result['levels'][0]['width'], 19)
            path = Path(directory) / 'scores.json'
            path.write_text('broken')
            scores = Scores(path)
            for score in range(15):
                self.assertTrue(scores.save('AB! long name 123', score))
            restored = Scores(path)
            self.assertEqual(len(restored.entries), 10)
            self.assertEqual(restored.entries[0][1], 14)
            self.assertTrue(all(len(n) <= 10 for n, _ in restored.entries))
            self.assertFalse(scores.save('bad', -1))


if __name__ == '__main__':
    unittest.main()
