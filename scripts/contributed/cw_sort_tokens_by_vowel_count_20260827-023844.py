"""Stable-sort basename tokens by vowel count (then original position)."""
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
    if len(t) >= 4 and all(t):
        rows.append((d, t))

for d, tokens in sorted(rows)[:50000]:
    reordered = [token for _, token in sorted(
        enumerate(tokens), key=lambda p: (sum(c in "aeiou" for c in p[1]), p[0]))]
    if reordered != tokens:
        candidate = d + "/" + "_".join(reordered)
        if candidate not in known:
            print(candidate)
