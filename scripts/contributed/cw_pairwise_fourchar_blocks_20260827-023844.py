"""Interleave paired basename strings in alternating four-character blocks."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8]
seeds = seeds[:300]
for d, a in seeds:
    for _, b in seeds:
        out = []
        for i in range(0, max(len(a), len(b)), 4):
            out.append(a[i:i+4]); out.append(b[i:i+4])
        candidate = d + "/" + "".join(out)
        if candidate not in names:
            print(candidate)
