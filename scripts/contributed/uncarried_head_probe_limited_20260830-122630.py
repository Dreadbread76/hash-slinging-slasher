"""Bounded probe of a large uncarried asset-family head."""
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
    parser.add_argument("head")
    parser.add_argument("--max-family", type=int, default=500)
    args = parser.parse_args()
    head = args.head.lower()
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES) if n.strip()}
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names() if n.strip())
    family = sorted(n for n in known if n.startswith(head))[:args.max_family]
    stems = set()
    reductions = dict(seams.REDUCTIONS)
    for name in family:
        for label in ("no head", "no ends", "no tail"):
            core = reductions[label](name)
            if len(core) >= 4:
                stems.add(core)
    with open(os.path.join(ROOT, "data", "suffixes.txt"), encoding="utf-8") as handle:
        endings = [line.strip().lower() for line in handle if line.strip()]
    candidates = {head + stem + ending for stem in stems for ending in endings}
    candidates.difference_update(known)
    print(f"{len(family):,} capped family seeds, {len(stems):,} stems, {len(candidates):,} candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)


if __name__ == "__main__":
    main()
