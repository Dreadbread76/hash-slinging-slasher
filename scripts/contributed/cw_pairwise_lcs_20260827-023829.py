"""Emit longest common subsequences from paired known basenames."""
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
def lcs(a, b):
    row = [""] * (len(b) + 1)
    for ca in a:
        prev = ""
        for j, cb in enumerate(b, 1):
            old = row[j]
            row[j] = prev + ca if ca == cb else (row[j] if len(row[j]) >= len(row[j-1]) else row[j-1])
            prev = old
    return row[-1]
for d, a in seeds:
    for _, b in seeds:
        out = lcs(a, b)
        if len(out) >= 4:
            candidate = d + "/" + out
            if candidate not in names:
                print(candidate)
