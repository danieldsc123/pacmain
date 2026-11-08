"""Produce a standalone native build and a platform-uploadable ZIP."""
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Bundle the local game, controls and editable config."""
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm',
                        '--clean', '--name', 'pac-man',
                        '--hidden-import', 'mazegenerator', 'pac-man.py'],
                       check=True)
        output = Path('dist/pac-man')
        for name in ('config.json', 'README.md'):
            shutil.copy2(name, output / name)
        (output / 'PLAY.txt').write_text(
            'Run ./pac-man config.json (Windows: pac-man.exe config.json).\n'
            'WASD/arrows: move; P: pause; F1: evaluation cheats.\n'
            'See README.md for configuration and all controls.\n')
        shutil.make_archive('dist/pac-man-native', 'zip', 'dist', 'pac-man')
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f'Packaging failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
