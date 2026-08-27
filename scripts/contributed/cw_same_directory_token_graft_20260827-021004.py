"""Graft a token from a different same-directory seed at every boundary.

This is deliberately distinct from token_edits: the inserted vocabulary is
borrowed from a sibling name rather than the position's observed token set.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
known = set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
by_dir = {}
for raw in known:
    n = raw.lower().replace("\\", "/")
    if "/" not in n or "." in n.rsplit("/", 1)[-1]:
        continue
    d, b = n.rsplit("/", 1)
    t = b.split("_")
    if len(t) < 3:
        continue
    by_dir.setdefault(d, []).append(t)

# Keep a measured, reproducible bound per directory; all four non-sound pools
# remain represented without turning this into an unbounded cross product.
for d in sorted(by_dir):
    seeds = sorted(by_dir[d])[:220]
    donors = sorted({x for row in seeds for x in row})
    for base in seeds:
        for tok in donors:
            if tok in base:
                continue
            for pos in range(1, len(base)):
                out = base[:pos] + [tok] + base[pos:]
                candidate = d + "/" + "_".join(out)
                if candidate not in known:
                    print(candidate)
