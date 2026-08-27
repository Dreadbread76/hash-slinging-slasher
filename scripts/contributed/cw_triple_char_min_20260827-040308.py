"""Combine triples of known basenames by position-wise character minimum."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8]
seeds = seeds[:45]
for d, a in seeds:
    for _, b in seeds:
        for _, c in seeds:
            out = "".join(min(x[i] for x in (a, b, c) if i < len(x)) for i in range(max(len(a), len(b), len(c))))
            candidate = d + "/" + out
            if candidate not in names:
                print(candidate)
