"""Recover compile-time concatenated asset literals from a public game-script dump.

    python contrib/source_literal_concats.py --root borrowed/bocw-source --size
    python contrib/source_literal_concats.py --root borrowed/bocw-source |
        bin\\windows\\confirm_list.exe - --label "Cold War source literal concatenations" \
        --script contrib/source_literal_concats.py

The direct source-literal pass reads quoted strings individually.  Game scripts also form asset
references by joining adjacent literal fragments (for example, an asset core plus a known suffix).
This emits only uninterrupted, compile-time literal concatenations; it never substitutes a
variable or invents a word.

Reads .gsc/.csc source files below --root.  Writes candidate names, one per line, to standard
output; --size reports the count only.  Reusable for a source dump not already mined this way.
"""
import argparse
import re
import sys
from pathlib import Path

RUN = re.compile(
    r'(?:#?"[A-Za-z0-9_./-]{1,160}"\s*\+\s*)+#?"[A-Za-z0-9_./-]{1,160}"'
)
STRING = re.compile(r'#?"([A-Za-z0-9_./-]{1,160})"')
LETTERS = re.compile(r'[A-Za-z]')


def plausible(value):
    return (
        6 <= len(value) <= 160
        and ("_" in value or "/" in value)
        and len(LETTERS.findall(value)) >= 3
        and not value.startswith(("function_", "hash_", "<dev"))
    )


def candidates(root):
    found = set()
    files = 0
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in {'.gsc', '.csc'}:
            continue
        files += 1
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError as error:
            print('skipping %s: %s' % (path, error), file=sys.stderr)
            continue
        for run in RUN.finditer(text):
            value = ''.join(STRING.findall(run.group())).lower()
            if plausible(value):
                found.add(value)
    print('%s source files -> %s literal concatenations' % (format(files, ','), format(len(found), ',')), file=sys.stderr)
    return found


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', default='borrowed/bocw-source')
    parser.add_argument('--size', action='store_true')
    options = parser.parse_args(argv)
    root = Path(options.root)
    if not root.is_dir():
        raise SystemExit('source dump not found: %s' % root)
    found = candidates(root)
    if options.size:
        return
    sys.stdout.write('\n'.join(sorted(found)))
    if found:
        sys.stdout.write('\n')


if __name__ == '__main__':
    main(sys.argv[1:])
