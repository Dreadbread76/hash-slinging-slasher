"""Rotate each complete basename right by three characters."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if len(b) < 6 or "." in b:
        continue
    out = b[-3:] + b[:-3]
    candidate = (d + "/" if d else "") + out
    if candidate != name:
        print(candidate)
