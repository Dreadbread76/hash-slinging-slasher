"""Reverse each contiguous digit run in known non-sound basenames."""
import os, re, sys
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
    d, sep, b = name.rpartition("/")
    if not sep:
        d, b = "", name
    if not re.search(r"\d{2,}", b) or "." in b:
        continue
    out = re.sub(r"\d+", lambda m: m.group(0)[::-1], b)
    candidate = (d + "/" if d else "") + out
    if candidate != name:
        print(candidate)
