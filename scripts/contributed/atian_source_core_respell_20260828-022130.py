"""Respell cores from the separate T8 Atian mod source with target-game decorations."""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "t8-atian-menu"
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./\\-]{5,159}")
QUOTED = re.compile(r'\"([^\"]{6,160})\"|\'([^\']{6,160})\'')
EXTENSIONS = {".gsc", ".txt", ".md", ".csv", ".ps1", ".json", ".conf", ".yml", ".yaml"}
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
TYPE_PREFIXES = ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_")


def source_names():
    names = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        values = [m.group() for m in TOKEN.finditer(text)]
        values += [m.group(1) or m.group(2) for m in QUOTED.finditer(text)]
        for value in values:
            value = value.strip().lower().replace("\\", "/")
            if ("_" in value or "/" in value) and sum(c.isalpha() for c in value) >= 3:
                names.add(value)
    return names


def core(value):
    directory, slash, stem = value.rpartition("/")
    stem = stem.rsplit(".", 1)[0] if "." in stem else stem
    for prefix in TYPE_PREFIXES:
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
            break
    return directory if slash else "", stem


def main():
    candidates = set()
    for value in source_names():
        directory, stem = core(value)
        if len(stem) < 4:
            continue
        for where in (directory, ""):
            lead = where + "/" if where else ""
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    candidates.add(lead + prefix + stem + suffix)
    for value in sorted(candidates):
        print(value)
    print(f"{len(candidates):,} T8 external-core respellings", file=sys.stderr)


if __name__ == "__main__":
    main()
