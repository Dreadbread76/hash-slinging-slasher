"""Seeded cross-name splice of basename token prefixes and suffixes."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
prefixes, suffixes = [], []
for n in paths:
    d, b = n.rsplit("/", 1)
    ts = b.split("_")
    if len(ts) < 3:
        continue
    for cut in range(1, len(ts) - 1):
        prefixes.append((d, "_".join(ts[:cut])))
        suffixes.append("_".join(ts[cut:]))
prefixes = sorted(set(prefixes))[:300]
suffixes = sorted(set(suffixes))[:300]
for d, p in prefixes:
    for s in suffixes:
        candidate = d + "/" + p + "_" + s
        if candidate not in names:
            print(candidate)
