"""Reorder basename tokens by descending token length, preserving stable ties."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    tokens = b.split("_")
    if len(tokens) < 3:
        continue
    out = sorted(enumerate(tokens), key=lambda x: (-len(x[1]), x[0]))
    candidate = (d + "/" if d else "") + "_".join(t for _, t in out)
    if candidate != name:
        print(candidate)
