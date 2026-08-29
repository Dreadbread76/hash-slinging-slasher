"""Interleave token positions from paired known BO4 non-sound names."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
tables = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*tables) if n.strip()}
for kind in ("model", "material", "image", "anim"):
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind=kind) if n.strip())
groups = {}
for name in known:
    directory, _, base = name.rpartition("/")
    parts = base.split("_")
    if len(parts) < 6 or "." in base:
        continue
    groups.setdefault((directory, len(parts)), []).append(parts)
out = set()
for (directory, _), values in groups.items():
    values.sort()
    for left, right in zip(values[:5000], values[1:5001]):
        merged = [left[i] if i % 2 == 0 else right[i] for i in range(len(left))]
        out.add((directory + "/" if directory else "") + "_".join(merged))
out.difference_update(known)
print(f"{len(known):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out):
    print(candidate)
