"""Adapta a interface do gerador atribuído sem modificá-lo."""
from collections import deque
from typing import Any

Point = tuple[int, int]
MOVES = ((0, -1, 1, 4), (1, 0, 2, 8),
         (0, 1, 4, 1), (-1, 0, 8, 2))


class Maze:
    """Representa as máscaras das paredes e as passagens recíprocas."""

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Gera e valida um labirinto pela interface do pacote externo."""
        from mazegenerator import MazeGenerator
        generator: Any = MazeGenerator(size=(width, height), perfect=False,
                                       seed=seed)
        self.cells: list[list[int]] = generator.maze
        self.width, self.height = width, height
        if len(self.cells) != height or any(len(row) != width
                                            for row in self.cells):
            raise ValueError('invalid generated dimensions')
        if any(type(cell) is not int or not 0 <= cell <= 15
               for row in self.cells for cell in row):
            raise ValueError('invalid generated wall masks')
        self.reachable = set(self.distances((0, 0)))
        if len(self.reachable) < 5:
            raise ValueError('too few reachable cells')
        self.center = self.nearest((width // 2, height // 2))
        self.corners = [self.nearest(p) for p in
                        ((0, 0), (width - 1, 0),
                         (0, height - 1), (width - 1, height - 1))]

    def neighbors(self, point: Point) -> list[Point]:
        """Retorna vizinhos com passagens recíprocas dentro dos limites."""
        x, y = point
        return [(x + dx, y + dy) for dx, dy, bit, opposite in MOVES
                if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                and not self.cells[y][x] & bit
                and not self.cells[y + dy][x + dx] & opposite]

    def distances(self, start: Point) -> dict[Point, int]:
        """Calcula as menores distâncias pelas passagens com busca em largura."""
        found = {start: 0}
        queue = deque([start])
        while queue:
            point = queue.popleft()
            for neighbor in self.neighbors(point):
                if neighbor not in found:
                    found[neighbor] = found[point] + 1
                    queue.append(neighbor)
        return found

    def nearest(self, target: Point) -> Point:
        """Encontra a célula acessível mais próxima do alvo geométrico."""
        return min(self.reachable, key=lambda p: (
            abs(p[0] - target[0]) + abs(p[1] - target[1]), p))
