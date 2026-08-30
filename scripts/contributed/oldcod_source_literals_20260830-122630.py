"""Emit asset-shaped literals from the early BO4/Cold War decompilation trees."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "borrowed" / "oldcod-source"
TARGETS = ("bo4_pre2017_vm31", "bo4_1.0.0_vm34", "bocw_pre2020_vm37", "bocw_1.0.0_vm37")
EXTENSIONS = {"", ".gsc", ".csc", ".cfg", ".csv", ".ddl", ".gdb", ".graph", ".raw", ".txt", ".json", ".md"}
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./\\-]{5,159}")
QUOTED = re.compile(r'''[\"']([^\"'\r\n]{6,160})[\"']''')


def keep(value):
    value = value.strip().lower().replace("\\", "/")
    if len(value) < 6 or len(value) > 160:
        return None
    if "_" not in value and "/" not in value:
        return None
    if sum(ch.isalpha() for ch in value) < 3:
        return None
    if value.startswith(("http://", "https://", "www.")):
        return None
    return value


def main():
    names = set()
    files = 0
    for target in TARGETS:
        root = SOURCE_ROOT / target
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
                continue
            files += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in TOKEN.finditer(text):
                value = keep(match.group())
                if value:
                    names.add(value)
            for match in QUOTED.finditer(text):
                value = keep(match.group(1))
                if value:
                    names.add(value)
    print(f"{files:,} early-source files -> {len(names):,} literals", file=sys.stderr)
    sys.stdout.write("\n".join(sorted(names)))
    if names:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
