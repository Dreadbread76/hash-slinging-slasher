"""Use a disjoint, corpus-measured decoration band on external BO4-source cores."""
import collections
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

SOURCE = ROOT / "borrowed" / "bo4-source"
TOKEN = re.compile(r'\"([A-Za-z0-9_./\\-]{6,160})\"')
EXTENSIONS = {".ai_htn", ".cfg", ".csc", ".csv", ".ddl", ".gdb", ".graph", ".gsc", ".raw", ".txt", ".vision"}
OLD_PREFIXES = {"", "i_", "mtl_", "xmodel_", "xanim_"}
OLD_SUFFIXES = {"", "_c", "_n", "_g", "_o", "_m", "_s", "_r"}


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


def decorations():
    tables = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
    heads, tails = collections.Counter(), collections.Counter()
    for table in tables:
        for value in snapshot.table_names(table):
            value = value.strip().lower().replace("\\", "/")
            directory, slash, base = value.rpartition("/")
            parts = base.split("_")
            if len(parts) < 3 or not parts[0] or not parts[-1]:
                continue
            head = (directory + "/" if slash else "") + parts[0] + "_"
            heads[head] += 1
            tails["_" + parts[-1]] += 1
    # Ranks 51-60 are intentionally disjoint from the common fixed decorations in the parent
    # method. They retain measured usage while probing less generic conventions.
    return ([p for p, _ in heads.most_common(100)[50:60]],
            [s for s, _ in tails.most_common(100)[50:60]])


def main():
    prefixes, suffixes = decorations()
    cores = source_names()
    candidates = 0
    for value in cores:
        _, _, stem = value.rpartition("/")
        stem = stem.rsplit(".", 1)[0] if "." in stem else stem
        if len(stem) < 4:
            continue
        for prefix in prefixes:
            for suffix in suffixes:
                print(prefix + stem + suffix)
                candidates += 1
    print(f"{len(cores):,} external cores x {len(prefixes):,} rare heads x "
          f"{len(suffixes):,} rare tails = {candidates:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
