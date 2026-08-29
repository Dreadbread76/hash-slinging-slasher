"""Emit character-multiset differences from paired known basenames."""
import os, sys
from collections import Counter
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
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8]
seeds = seeds[:300]
for d, a in seeds:
    ca = Counter(a)
    for _, b in seeds:
        cb = Counter(b)
        out = []
        for ch in sorted(ca):
            out.append(ch * max(0, ca[ch] - cb[ch]))
        candidate = d + "/" + "".join(out)
        if len(candidate.rsplit("/", 1)[-1]) >= 4 and candidate not in names:
            print(candidate)
