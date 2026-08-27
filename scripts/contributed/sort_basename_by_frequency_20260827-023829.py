"""Stable reorder of basename characters by increasing per-name frequency."""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if len(b) < 4 or "." in b:
        continue
    counts = Counter(b)
    out = "".join(ch for _, ch in sorted(enumerate(b), key=lambda x: (counts[x[1]], x[0])))
    candidate = (d + "/" if d else "") + out
    if candidate != name:
        print(candidate)
