"""Swap edge characters of each directory component; preserve basename."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    n = name.lower().replace("\\", "/")
    if "/" not in n:
        continue
    d, b = n.rsplit("/", 1)
    if "." in b:
        continue
    parts = [p[-1] + p[1:-1] + p[0] if len(p) >= 2 else p for p in d.split("/")]
    candidate = "/".join(parts) + "/" + b
    if candidate != n and candidate not in names:
        print(candidate)
