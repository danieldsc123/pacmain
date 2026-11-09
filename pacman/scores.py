"""Salva o ranking de forma atômica e tolerante a falhas."""
import json
import logging
import os
import tempfile
from pathlib import Path


def name_clean(name: str) -> str:
    """Mantém até dez caracteres alfanuméricos e espaços."""
    return ''.join(c for c in name if c.isalnum() or c == ' ')[:10].strip()


class Scores:
    """Mantém as dez maiores pontuações válidas."""

    def __init__(self, path: Path) -> None:
        """Lê os registros e tolera arquivos ausentes ou corrompidos."""
        self.path = path
        self.entries: list[tuple[str, int]] = []
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, list):
                raise ValueError('scores must be a list')
            for row in data:
                if not isinstance(row, dict):
                    continue
                name, score = row.get('name'), row.get('score')
                if (isinstance(name, str) and name_clean(name) == name
                        and name and type(score) is int and score >= 0):
                    self.entries.append((name, score))
            self.entries = sorted(self.entries, key=lambda r: -r[1])[:10]
        except FileNotFoundError:
            pass
        except (OSError, ValueError, UnicodeError) as exc:
            logging.warning('Cannot read highscores: %s', exc)

    def save(self, name: str, score: int) -> bool:
        """Adiciona uma pontuação e substitui a tabela em disco de forma atômica."""
        if type(score) is not int or score < 0:
            return False
        self.entries.append((name_clean(name) or 'Player', score))
        self.entries = sorted(self.entries, key=lambda r: -r[1])[:10]
        temporary = ''
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=self.path.parent,
                                             delete=False) as stream:
                temporary = stream.name
                json.dump([{'name': n, 'score': s}
                           for n, s in self.entries], stream)
            os.replace(temporary, self.path)
            return True
        except OSError as exc:
            logging.warning('Cannot save highscores: %s', exc)
            return False
        finally:
            if temporary and os.path.exists(temporary):
                try:
                    os.unlink(temporary)
                except OSError:
                    pass
