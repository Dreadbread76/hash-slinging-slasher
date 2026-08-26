"""Recover asset-like literals from a public Black Ops 4 source dump.

    python contrib/bo4_source_literals.py --root borrowed/bo4-source |
        target/release/confirm_list.exe - --game BLKOPS04 \
        --label "Black Ops 4 source literals" --script contrib/bo4_source_literals.py

The dump is an external source, not a naming relation derived from the hash tables. It contains
decompiled GSC/CSC and game data files whose quoted strings include asset references. This script
only emits plausible literals; `confirm_list` verifies every row against the BO4 snapshot and
excludes names the community already knows.

The source tree stays in `borrowed/` because it is reproducible external input. The generator is
the artifact that should travel with any finding.
"""
import argparse
import re
import sys
from pathlib import Path


LITERAL = re.compile(r'(?:#)?"([A-Za-z0-9_./-]{6,160})"')
LETTERS = re.compile(r'[A-Za-z]')
EXTENSIONS = {
    '.ai_htn', '.cfg', '.csc', '.csv', '.ddl', '.gdb', '.graph', '.gsc', '.raw', '.txt', '.vision'
}
NOISE_PREFIXES = ('function_', 'hash_', 'var_')


def plausible(value):
    if value.startswith(NOISE_PREFIXES):
        return False
    if '_' not in value and '/' not in value:
        return False
    return len(LETTERS.findall(value)) >= 3


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', default='borrowed/bo4-source',
                        help='root of the public BO4 source dump')
    options = parser.parse_args(argv)

    root = Path(options.root)
    if not root.is_dir():
        raise SystemExit(f'BO4 source dump not found: {root}')

    names = set()
    files = 0
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        files += 1
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError as error:
            print(f'skipping {path}: {error}', file=sys.stderr)
            continue
        for value in LITERAL.findall(text):
            value = value.lower()
            if plausible(value):
                names.add(value)

    print(f'{files:,} source files -> {len(names):,} name-shaped literals', file=sys.stderr)
    sys.stdout.write('\n'.join(sorted(names)))
    if names:
        sys.stdout.write('\n')


if __name__ == '__main__':
    main(sys.argv[1:])
