"""Probe one uncarried asset-family head using its own observed core vocabulary."""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import seams
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("head", help="uncarried leading family, including trailing underscore")
    args = parser.parse_args()
    head = args.head.lower()
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES) if n.strip()}
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names() if n.strip())
    family = [n for n in known if n.startswith(head)]
    reductions = dict(seams.REDUCTIONS)
    stems = set()
    for name in family:
        for label in ("no head", "no ends", "no tail"):
            core = reductions[label](name)
            if len(core) >= 4:
                stems.add(core)
    endings = [line.strip().lower() for line in open(os.path.join(ROOT, "data", "suffixes.txt"), encoding="utf-8") if line.strip()]
    candidates = set()
    for stem in stems:
        for ending in endings:
            candidate = head + stem + ending
            if candidate not in known:
                candidates.add(candidate)
    print(f"{len(family):,} family seeds, {len(stems):,} stems, {len(candidates):,} candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)


if __name__ == "__main__":
    main()
