"""Combine a basename with a reversed second basename as a seeded pair."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if n.rsplit("/", 1)[1].count("_") >= 2]
seeds = seeds[:300]
for d, a in seeds:
    for _, b in seeds:
        candidate = d + "/" + a + "_" + b[::-1]
        if candidate not in names:
            print(candidate)
