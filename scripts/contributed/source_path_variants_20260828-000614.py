"""Emit asset-shaped variants of real paths in an external game-source tree.

The quoted-literal searches do not cover names that occur only as source filenames.  This keeps
the vocabulary grounded in the dump: relative path, basename, and directory/basename forms with
the source extension removed.  It deliberately emits no invented tokens.
"""
import argparse
from pathlib import Path
import re

EXTENSIONS = {".gsc", ".csc", ".cfg", ".csv", ".ddl", ".gdb", ".graph", ".raw", ".vision", ".txt", ".ai_htn"}
WORD = re.compile(r"[a-z]")


def plausible(value):
    return (6 <= len(value) <= 180 and ("_" in value or "/" in value)
            and len(WORD.findall(value)) >= 3)


def candidates(root):
    found = set()
    files = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        files += 1
        rel = path.relative_to(root).as_posix().lower()
        stem = rel[: -len(path.suffix)]
        base = path.stem.lower()
        values = {stem, base}
        if "/" in stem:
            directory, _, name = stem.rpartition("/")
            values.add(directory + "/" + name)
        for value in values:
            if plausible(value):
                found.add(value)
    print(f"{files:,} source files -> {len(found):,} path variants", file=__import__("sys").stderr)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--size", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"source dump not found: {root}")
    values = candidates(root)
    if not args.size:
        print("\n".join(sorted(values)))


if __name__ == "__main__":
    main()
