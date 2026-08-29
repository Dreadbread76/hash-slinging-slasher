"""Move the observed basename before its directory prefix."""
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
