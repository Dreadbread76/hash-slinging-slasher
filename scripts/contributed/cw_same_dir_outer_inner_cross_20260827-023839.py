"""Cross same-directory seeds: outer tokens from A, interior block from B."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot

tables = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xmodels", "fnv1a_xanims")
known = set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
groups = {}
for raw in known:
    n = raw.lower().replace("\\", "/")
    if "/" not in n or "." in n.rsplit("/", 1)[-1]:
        continue
    d, b = n.rsplit("/", 1)
    t = b.split("_")
    if len(t) >= 5 and all(t):
        groups.setdefault((d, len(t)), []).append(t)

for (d, width), rows in sorted(groups.items()):
    rows = sorted(rows)[:180]
    for a in rows:
        for b in rows:
            if a == b:
                continue
            # Preserve A's family framing while borrowing B's complete core.
            out = [a[0]] + b[1:-1] + [a[-1]]
            candidate = d + "/" + "_".join(out)
            if candidate not in known:
                print(candidate)
