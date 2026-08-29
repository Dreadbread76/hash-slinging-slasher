"""Swap first and middle characters of interior tokens in BO4 non-sound assets."""
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
out = set()
for name in known:
    directory, _, base = name.rpartition("/")
    parts = base.split("_")
    if len(parts) < 4 or "." in base:
        continue
    changed = parts[:]
    for i in range(1, len(parts) - 1):
        token = list(parts[i])
        if len(token) > 2:
            middle = len(token) // 2
            token[0], token[middle] = token[middle], token[0]
            changed[i] = "".join(token)
    out.add((directory + "/" if directory else "") + "_".join(changed))
out.difference_update(known)
print(f"{len(known):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out): print(candidate)
