"""Valida a configuração JSON com suporte a comentários."""
import json
import logging
from pathlib import Path
from typing import Any

DEFAULTS = {'lives': 3, 'points_per_pacgum': 10,
            'points_per_super_pacgum': 50, 'points_per_ghost': 200,
            'seed': 42, 'level_max_time': 90, 'power_seconds': 8,
            'ghost_respawn_seconds': 5, 'player_speed': 7, 'ghost_speed': 4}


def integer(value: Any, default: int, low: int, high: int) -> int:
    """Valida configurações inteiras dentro dos limites permitidos."""
    if type(value) is not int or not low <= value <= high:
        logging.warning('Invalid value %r; using %s', value, default)
        return default
    return int(value)


def load(path: Path) -> dict[str, Any]:
    """Usa valores padrão para arquivos ilegíveis e configurações inválidas."""
    raw: dict[str, Any] = {}

    try:
        if path.suffix.lower() != '.json':
            raise ValueError('expected a .json file')

        data = json.loads('\n'.join(
            line for line in path.read_text().splitlines()
            if not line.lstrip().startswith('#')))

        if not isinstance(data, dict):
            raise ValueError('expected a JSON object')
        raw = data
    except (OSError, ValueError, UnicodeError) as exc:
        logging.warning('Configuration: %s; using defaults', exc)
    result: dict[str, Any] = {}
    for key, default in DEFAULTS.items():
        low = 0 if key.startswith('points_') else 1
        high = 999999 if key.startswith('points_') else 3600
        if key in ('lives', 'player_speed', 'ghost_speed'):
            high = 20
        result[key] = integer(raw.get(key, default), default, low, high)
    filename = raw.get('highscore_filename', 'highscores.json')
    if not isinstance(filename, str) or not filename.strip():
        logging.warning('Invalid highscore_filename; using default')
        filename = 'highscores.json'
    result['highscore_filename'] = str(path.parent / filename)
    levels = raw.get('levels', raw.get('level', [{} for _ in range(10)]))
    if not isinstance(levels, list) or not levels:
        logging.warning('Invalid levels; using defaults')
        levels = []
    if len(levels) < 10:
        logging.warning('Padding levels to the required minimum of 10')
        levels = levels + [{} for _ in range(10 - len(levels))]
    result['levels'] = []
    for item in levels[:100]:
        row = item if isinstance(item, dict) else {}
        timeout = row.get('level_max_time', result['level_max_time'])
        result['levels'].append({
            'width': integer(row.get('width', 19), 19, 9, 35),
            'height': integer(row.get('height', 15), 15, 9, 25),
            'level_max_time': integer(timeout, result['level_max_time'],
                                      1, 3600)})
    return result
