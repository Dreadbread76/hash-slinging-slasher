"""Hash asset-shaped literals and identifiers from borrowed T7/T8 mod source.

The borrowed mod repositories are external to the retail-source harvests. This pass tests their
literal spellings directly, preserving paths and punctuation that the game may use in names.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPORA = (ROOT / "borrowed" / "bo4-lucy-menu", ROOT / "borrowed" / "t8-atian-menu")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./\\-]{5,159}")
QUOTED = re.compile(r'\"([^\"]{6,160})\"|\'([^\']{6,160})\'')
EXTENSIONS = {".gsc", ".txt", ".md", ".csv", ".ps1", ".json", ".conf", ".yml", ".yaml"}


def keep(value):
    value = value.strip().lower().replace("\\", "/")
    if len(value) < 6 or len(value) > 160 or "_" not in value and "/" not in value:
        return None
    if sum(ch.isalpha() for ch in value) < 3:
        return None
    if value.startswith(("http://", "https://", "www.")):
        return None
    return value


def main():
    out = set()
    files = 0
    for corpus in CORPORA:
        if not corpus.exists():
            continue
        for path in corpus.rglob("*"):
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
                    out.add(value)
            for match in QUOTED.finditer(text):
                value = keep(match.group(1) or match.group(2))
                if value:
                    out.add(value)
    for value in sorted(out):
        print(value)
    print(f"{files:,} files -> {len(out):,} literals", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
