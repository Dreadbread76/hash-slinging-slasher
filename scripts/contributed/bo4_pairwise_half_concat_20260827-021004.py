"""Combine first/second token halves from paired BO4 non-sound names."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent
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
        cut = len(left) // 2
        merged = left[:cut] + right[cut:]
        out.add((directory + "/" if directory else "") + "_".join(merged))
out.difference_update(known)
print(f"{len(known):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out): print(candidate)
