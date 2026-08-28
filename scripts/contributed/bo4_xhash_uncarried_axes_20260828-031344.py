"""Apply uncarried semantic prefixes and fresh measured tails to BO4 xhash cores."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source" / "tables" / "data" / "xhash"

PREFIXES = ("reflex_", "acog_", "lut_mp_", "ui_", "loot_", "weapon_")
SUFFIXES = ("_view", "_world", "_metal", "_decal", "_proxy", "_maps1", "_maps2", "_red", "_white", "_wet", "_glass", "_black")


def cores():
    found = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            value = raw.strip().lower().replace("\\", "/")
            if not value or value.startswith("hash_") or ("_" not in value and "/" not in value):
                continue
            stem = value.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            for prefix in ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_"):
                if stem.startswith(prefix):
                    stem = stem[len(prefix):]
                    break
            if len(stem) >= 4:
                found.add(stem)
    return sorted(found)


def main():
    count = 0
    for stem in cores():
        for prefix in PREFIXES:
            for suffix in SUFFIXES:
                print(prefix + stem + suffix)
                count += 1
    print(f"{count:,} streamed uncarried-axis xhash respellings", file=sys.stderr)


if __name__ == "__main__":
    main()
