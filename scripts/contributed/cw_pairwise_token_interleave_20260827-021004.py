"""Interleave token positions from pairs of known non-sound basenames."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = []
for n in paths:
    d, b = n.rsplit("/", 1)
    t = b.split("_")
    if len(t) >= 3:
        seeds.append((d, t))
seeds = seeds[:300]
for d, a in seeds:
    for _, b in seeds:
        out = []
        for i in range(max(len(a), len(b))):
            if i < len(a): out.append(a[i])
            if i < len(b): out.append(b[i])
        candidate = d + "/" + "_".join(out)
        if candidate not in names:
            print(candidate)
