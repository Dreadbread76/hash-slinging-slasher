"""Increment every basename digit modulo ten in known non-sound names."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if not any(c.isdigit() for c in b) or "." in b:
        continue
    out = "".join(str((int(c) + 1) % 10) if c.isdigit() else c for c in b)
    candidate = (d + "/" if d else "") + out
    if candidate != name:
        print(candidate)
