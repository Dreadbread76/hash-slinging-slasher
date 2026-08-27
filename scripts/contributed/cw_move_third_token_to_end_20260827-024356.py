"""Move the third basename token to the end, preserving all other order."""
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
    out = tokens[:2] + tokens[3:] + [tokens[2]]
    candidate = d + "/" + "_".join(out)
    if candidate not in known:
        print(candidate)
