"""Reverse both token order and characters within each token."""
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
    if len(tokens) < 2 or any(len(t) < 2 for t in tokens):
        continue
    candidate = (d + "/" if d else "") + "_".join(t[::-1] for t in tokens[::-1])
    if candidate != name:
        print(candidate)
