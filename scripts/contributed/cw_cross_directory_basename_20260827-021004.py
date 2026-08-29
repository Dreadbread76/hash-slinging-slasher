"""Seeded recombination: pair observed directories with basenames from other names."""
import os, sys
_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
dirs = sorted(set(n.rsplit("/", 1)[0] for n in paths))
bases = sorted(set(n.rsplit("/", 1)[1] for n in paths if n.rsplit("/", 1)[1].count("_") >= 2))
dirs = dirs[:1200]
bases = bases[:1200]
for d in dirs:
    for b in bases:
        candidate = d + "/" + b
        if candidate not in names:
            print(candidate)
