"""Fill evidence-backed head_axis_tail family grids without requiring shared tails."""
import collections
import pathlib
import sys
import argparse
ROOT = pathlib.Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages",
          "fnv1a_ximages_v2", "fnv1a_xmodels", "fnv1a_xanims", "fnv1a_xanims_v2")
have = {n.lower() for n in snapshot.table_names(*TABLES)} | {n.lower() for n in snapshot.confirmed_names()}
groups = collections.defaultdict(list)
for name in have:
    if name.count("_") >= 2 and all(c not in name for c in "/.\\"):
        p = name.split("_", 2)
        if len(p) == 3 and p[1] and p[2]:
            groups[p[0]].append((p[1], p[2]))
ranked = []
for head, pairs in groups.items():
    axes = {a for a, _ in pairs}; tails = {t for _, t in pairs}
    if len(pairs) >= 200 and len(axes) >= 3 and len(tails) >= 20:
        ranked.append((len(axes) * len(tails), head, axes, tails))
ranked.sort(reverse=True)
ap = argparse.ArgumentParser(); ap.add_argument('--size', action='store_true'); ap.add_argument('--top', type=int, default=8); ap.add_argument('--cap', type=int, default=50_000_000); args = ap.parse_args()
seen = set(); cap = args.cap
for _, head, axes, tails in ranked[:args.top]:
    for axis in sorted(axes):
        for tail in sorted(tails):
            if len(seen) >= cap: break
            candidate = f"{head}_{axis}_{tail}"
            if candidate not in have:
                seen.add(candidate)
        if len(seen) >= cap: break
    if len(seen) >= cap: break
print(f"{len(ranked)} families, {len(seen)} unseen cells", file=sys.stderr)
if not args.size:
    for candidate in sorted(seen): print(candidate)
