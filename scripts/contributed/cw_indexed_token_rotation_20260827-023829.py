"""Rotate each basename token by its position, yielding one indexed variant."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
known = set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
rows = []
for raw in known:
    n = raw.lower().replace("\\", "/")
    if "/" not in n or "." in n.rsplit("/", 1)[-1]:
        continue
    d, b = n.rsplit("/", 1)
    t = b.split("_")
    if len(t) >= 4:
        rows.append((d, t))

for d, tokens in sorted(rows)[:50000]:
    out = []
    changed = False
    for i, token in enumerate(tokens):
        if len(token) > 1:
            k = i % len(token)
            out.append(token[k:] + token[:k])
            changed |= k != 0
        else:
            out.append(token)
    if changed:
        candidate = d + "/" + "_".join(out)
        if candidate not in known:
            print(candidate)
