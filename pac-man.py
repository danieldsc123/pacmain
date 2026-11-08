#!/usr/bin/env python3
"""Command-line entry point for the Pac-Man arcade game."""
import logging
import sys
from pathlib import Path


def main() -> int:
    """Validate invocation and report startup errors without tracebacks."""
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    if len(sys.argv) != 2:
        print('Usage: python3 pac-man.py config.json', file=sys.stderr)
        return 2
    try:
        from pacman.config import load
        from pacman.ui import App
        App(load(Path(sys.argv[1]))).run()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f'Cannot start Pac-Man: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
