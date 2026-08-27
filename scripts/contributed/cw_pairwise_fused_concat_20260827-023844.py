"""Fuse complete basename pairs without a separator, using the second directory."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if n.rsplit("/", 1)[1].count("_") >= 2]
seeds = seeds[:300]
for _, a in seeds:
    for d, b in seeds:
        candidate = d + "/" + a + b
        if candidate not in names:
            print(candidate)
