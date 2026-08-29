"""Extract actual .snd paths from the BO4 source dump for unfolded sound confirmation."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source"
PATH = re.compile(r"[A-Za-z0-9_./-]{6,180}\.([A-Za-z0-9]+)\.snd", re.IGNORECASE)
EXTENSIONS = {".gsc", ".csc", ".csv", ".ddl", ".txt", ".raw", ".gdb", ".cfg", ".vision"}


def main():
    names = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            body = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in PATH.finditer(body):
            value = match.group().lower().replace("/", "\\")
            if "\\" in value and sum(ch.isalpha() for ch in value) >= 3:
                names.add(value)
    for name in sorted(names):
        print(name)
    print(f"{len(names):,} unfolded source sound paths", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
