"""Respell external BO4-source cores with common measured target decorations."""
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


def decorations():
    heads, tails = collections.Counter(), collections.Counter()
    for table in TABLES:
        for value in snapshot.table_names(table):
            value = value.strip().lower().replace("\\", "/")
            directory, slash, base = value.rpartition("/")
            parts = base.split("_")
            if len(parts) < 3 or not parts[0] or not parts[-1]:
                continue
            heads[((directory + "/") if slash else "") + parts[0] + "_"] += 1
            tails["_" + parts[-1]] += 1
    # The earlier 10x10 ranks 51-60 pass is disjoint. This pass uses common measured target
    # decorations, but retains full directory-bearing prefixes absent from the fixed pass.
    return ([p for p, _ in heads.most_common(20)],
            [s for s, _ in tails.most_common(50)])


def main():
    prefixes, suffixes = decorations()
    cores = source_names()
    count = 0
    for value in sorted(cores):
        _, _, stem = value.rpartition("/")
        stem = stem.rsplit(".", 1)[0] if "." in stem else stem
        if len(stem) < 4:
            continue
        for prefix in prefixes:
            for suffix in suffixes:
                print(prefix + stem + suffix)
                count += 1
    print(f"{len(cores):,} external cores x {len(prefixes):,} common heads x "
          f"{len(suffixes):,} common tails = {count:,} streamed candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
