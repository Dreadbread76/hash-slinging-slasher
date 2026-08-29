"""Preserve external source directories while applying measured target decorations."""
import collections
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "contrib"))
import snapshot
from bo4_source_core_rare_decor_20260829 import source_names

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")


def target_decorations():
    heads, tails = collections.Counter(), collections.Counter()
    for table in TABLES:
        for value in snapshot.table_names(table):
            value = value.strip().lower().replace("\\", "/")
            _, _, base = value.rpartition("/")
            parts = base.split("_")
            if len(parts) < 3 or not parts[0] or not parts[-1]:
                continue
            heads[parts[0] + "_"] += 1
            tails["_" + parts[-1]] += 1
    return ([p for p, _ in heads.most_common(20)],
            [s for s, _ in tails.most_common(50)])


def main():
    prefixes, suffixes = target_decorations()
    count = 0
    for value in sorted(source_names()):
        directory, slash, stem = value.rpartition("/")
        stem = stem.rsplit(".", 1)[0] if "." in stem else stem
        if not directory or len(stem) < 4:
            continue
        lead = directory + "/"
        for prefix in prefixes:
            for suffix in suffixes:
                print(lead + prefix + stem + suffix)
                count += 1
    print(f"directory-preserved external cores x {len(prefixes):,} heads x "
          f"{len(suffixes):,} tails = {count:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
