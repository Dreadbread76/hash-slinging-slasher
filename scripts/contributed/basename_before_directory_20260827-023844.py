"""Move the observed basename before its directory prefix."""
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
    if "." in b or not d:
        continue
    candidate = b + "/" + d
    if candidate not in names:
        print(candidate)
