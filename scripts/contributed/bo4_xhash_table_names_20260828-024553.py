"""Extract unquoted asset names from the BO4 source dump's xhash tables."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source" / "tables" / "data" / "xhash"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./\\-]{5,180}$")


def main():
    names = set()
    files = 0
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        files += 1
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            value = line.strip().lower()
            if not NAME.fullmatch(value) or value.startswith("hash_"):
                continue
            if "_" not in value and "/" not in value:
                continue
            if sum(ch.isalpha() for ch in value) < 3:
                continue
            names.add(value)
    for value in sorted(names):
        print(value)
    print(f"{files:,} xhash files -> {len(names):,} unquoted asset names", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
