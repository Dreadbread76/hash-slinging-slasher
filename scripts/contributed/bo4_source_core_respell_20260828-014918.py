"""Respell external BO4-source cores with measured target asset decorations."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source"
TOKEN = re.compile(r'\"([A-Za-z0-9_./\\-]{6,160})\"')
EXTENSIONS = {".ai_htn", ".cfg", ".csc", ".csv", ".ddl", ".gdb", ".graph", ".gsc", ".raw", ".txt", ".vision"}
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
        for match in TOKEN.finditer(text):
            value = match.group(1).lower().replace("\\", "/")
            if ("_" in value or "/" in value) and sum(c.isalpha() for c in value) >= 3:
                names.add(value)
    return names


def core(value):
    directory, slash, base = value.rpartition("/")
    stem = base.rsplit(".", 1)[0] if "." in base else base
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
            lead = (where + "/") if where else ""
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    candidates.add(lead + prefix + stem + suffix)
    for value in sorted(candidates):
        print(value)
    print(f"{len(candidates):,} respelled external-core candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
