"""Normalize unquoted Cold War source identifiers into asset-style names."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bocw-source"
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{5,}")
CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def main():
    found = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.stat().st_size > 8_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for raw in IDENT.findall(text):
            if "_" not in raw and not CAMEL.search(raw):
                continue
            value = CAMEL.sub("_", raw).lower()
            value = re.sub(r"_+", "_", value).strip("_")
            if len(value) >= 8 and "__" not in value:
                found.add(value)
    for value in sorted(found):
        print(value)
    print(f"{len(found):,} normalized source identifiers", file=sys.stderr)


if __name__ == "__main__":
    main()
