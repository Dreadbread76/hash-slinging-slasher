"""Drop the first component from multi-level observed paths."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
for name in sorted(names):
    n = name.lower().replace("\\", "/")
    parts = n.split("/")
    if len(parts) < 3 or "." in parts[-1]:
        continue
    candidate = "/".join(parts[1:])
    if candidate not in names:
        print(candidate)
