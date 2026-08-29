"""Combine triples via median of 5-bit rotated alphabet indices."""
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
seeds = [(n.rsplit("/", 1)[0], n.rsplit("/", 1)[1]) for n in paths if len(n.rsplit("/", 1)[1]) >= 8][:45]
def rot(v): return ((v << 1) | (v >> 4)) & 31
for d, a in seeds:
    for _, b in seeds:
        for _, c in seeds:
            out = []
            for i in range(max(len(a), len(b), len(c))):
                vals = [x[i] for x in (a, b, c) if i < len(x)]
                if len(vals) == 3 and all(v.isalpha() for v in vals):
                    nums = sorted(rot(ord(v)-96) for v in vals)
                    out.append(chr(97 + nums[1] % 26))
                else: out.append(vals[0])
            candidate = d + "/" + "".join(out)
            if candidate not in names: print(candidate)
