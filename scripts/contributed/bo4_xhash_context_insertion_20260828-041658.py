"""Insert xhash table context tokens around external cores before respelling."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source" / "tables" / "data" / "xhash"
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
TYPE_PREFIXES = ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_")


def pairs():
    found = set()
    for path in SOURCE.rglob("*.txt"):
        context = path.stem.lower()
        if "_" in context:
            context = context.split("_", 1)[1]
        if context in {"common", "core", "frontend", "ui", "mp", "zm"}:
            context = path.stem.lower()
            context = context.replace("core_", "").replace("mp_", "").replace("zm_", "")
        if not context or len(context) > 28:
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
                found.add((context, stem))
    return sorted(found)


def main():
    count = 0
    for context, stem in pairs():
        for core in (context + "_" + stem, stem + "_" + context):
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    print(prefix + core + suffix)
                    count += 1
    print(f"{count:,} streamed xhash context insertions", file=sys.stderr)


if __name__ == "__main__":
    main()
