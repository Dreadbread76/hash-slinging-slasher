"""BO4 non-sound numeric repadding: change one numeric run's zero padding."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
RUN = re.compile(r"(?<![0-9])([0-9]+)(?![0-9])")
known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES) if n.strip()}
for kind in ("model", "material", "image", "anim"):
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind=kind) if n.strip())
seen = set()
for name in known:
    for match in RUN.finditer(name):
        digits = match.group(1)
        value = digits.lstrip("0") or "0"
        if len(value) > 4:
            continue
        for width in (1, 2, 3, 4):
            padded = value.zfill(width)
            if padded == digits:
                continue
            candidate = name[:match.start()] + padded + name[match.end():]
            if candidate not in known and candidate not in seen:
                seen.add(candidate)
                print(candidate)
print(f"{len(seen):,} candidates", file=sys.stderr)
