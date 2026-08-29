"""Reverse each contiguous digit run in known non-sound basenames."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
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
