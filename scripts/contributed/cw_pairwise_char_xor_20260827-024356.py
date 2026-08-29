"""Combine paired basename letters position-wise with XOR-derived letters."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
names = set(snapshot.table_names(*tables)); names.update(snapshot.confirmed_names())
paths = sorted(n.lower().replace("\\", "/") for n in names if "/" in n and "." not in n.rsplit("/", 1)[-1])
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8]
seeds = seeds[:300]
def combine(a, b):
    out = []
    for i in range(max(len(a), len(b))):
        if i >= len(a): out.append(b[i]); continue
        if i >= len(b): out.append(a[i]); continue
        x, y = a[i], b[i]
        if x.isalpha() and y.isalpha():
            out.append(chr(97 + ((ord(x)-97) ^ (ord(y)-97)) % 26))
        else:
            out.append(x)
    return "".join(out)
for d, a in seeds:
    for _, b in seeds:
        candidate = d + "/" + combine(a, b)
        if candidate not in names:
            print(candidate)
