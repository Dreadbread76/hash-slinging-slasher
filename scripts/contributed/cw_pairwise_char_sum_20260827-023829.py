"""Combine paired basename letters position-wise using modular alphabet sums."""
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
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8]
seeds = seeds[:300]
def combine(a, b):
    out = []
    for i in range(max(len(a), len(b))):
        x, y = (ord(a[i]) if i < len(a) else 0), (ord(b[i]) if i < len(b) else 0)
        if i < len(a) and i < len(b) and a[i].isalpha() and b[i].isalpha():
            out.append(chr((ord("a") + (ord(a[i])-97 + ord(b[i])-97)) % 26 + 97))
        elif i < len(a):
            out.append(a[i])
        elif i < len(b):
            out.append(b[i])
    return "".join(out)
for d, a in seeds:
    for _, b in seeds:
        out = combine(a, b)
        candidate = d + "/" + out
        if candidate not in names:
            print(candidate)
