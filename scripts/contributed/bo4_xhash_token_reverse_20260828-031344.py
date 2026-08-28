"""Reverse underscore-token order in external BO4 xhash cores, then respell."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source" / "tables" / "data" / "xhash"
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
TYPE_PREFIXES = ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_")


def cores():
    found = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            value = raw.strip().lower().replace("\\", "/")
            if not value or value.startswith("hash_"):
                continue
            stem = value.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            for prefix in TYPE_PREFIXES:
                if stem.startswith(prefix):
                    stem = stem[len(prefix):]
                    break
            if len(stem) >= 4 and "_" in stem:
                found.add(stem)
    return sorted(found)


def main():
    count = 0
    for stem in cores():
        reversed_stem = "_".join(reversed(stem.split("_")))
        for prefix in PREFIXES:
            for suffix in SUFFIXES:
                print(prefix + reversed_stem + suffix)
                count += 1
    print(f"{count:,} streamed reversed-token xhash respellings", file=sys.stderr)


if __name__ == "__main__":
    main()
