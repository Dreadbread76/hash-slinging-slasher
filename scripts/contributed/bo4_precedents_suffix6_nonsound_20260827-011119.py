"""Six-token contextual precedent swaps over BO4 non-sound asset names only."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
import precedents_suffix6

def known_names():
    tables = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
    values = set()
    for table in tables:
        values.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table) if n.strip())
    for kind in ("model", "material", "image", "anim"):
        values.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind=kind) if n.strip())
    return values

precedents_suffix6.precedents.known_names = known_names
raise SystemExit(precedents_suffix6.main(sys.argv[1:]))
