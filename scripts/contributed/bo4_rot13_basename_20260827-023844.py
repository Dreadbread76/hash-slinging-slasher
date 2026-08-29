"""Apply ROT13 to known BO4 non-sound basenames."""
import codecs, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
tables = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*tables) if n.strip()}
for kind in ("model", "material", "image", "anim"):
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind=kind) if n.strip())
out = set()
for name in known:
    directory, _, base = name.rpartition("/")
    if len(base) < 5 or "." in base:
        continue
    out.add((directory + "/" if directory else "") + codecs.decode(base, "rot_13"))
out.difference_update(known)
print(f"{len(known):,} seeds, {len(out):,} candidates", file=sys.stderr)
for candidate in sorted(out): print(candidate)
