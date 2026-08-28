"""Combine a real source filename with asset-shaped literals found in that same file."""
import argparse
import re
from pathlib import Path
import sys

LITERAL = re.compile(r'(?:#)?"([A-Za-z0-9_./-]{3,120})"')
EXTENSIONS = {".gsc", ".csc", ".cfg", ".csv", ".ddl", ".gdb", ".graph", ".raw", ".vision", ".txt", ".ai_htn"}


def plausible(value):
    return len(value) >= 4 and ("_" in value or "/" in value) and sum(c.isalpha() for c in value) >= 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--size", action="store_true")
    args = ap.parse_args()
    root = Path(args.root)
    found = set()
    files = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        files += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_stem = path.stem.lower()
        if not plausible(file_stem):
            continue
        literals = {v.lower() for v in LITERAL.findall(text) if plausible(v.lower())}
        for literal in literals:
            base = literal.rsplit("/", 1)[-1]
            if plausible(base):
                found.add(file_stem + "_" + base)
                found.add(base + "_" + file_stem)
            found.add(file_stem + "/" + literal)
            found.add(literal + "/" + file_stem)
    print(f"{files:,} source files -> {len(found):,} same-file context candidates", file=sys.stderr)
    if not args.size:
        print("\n".join(sorted(found)))


if __name__ == "__main__":
    main()
