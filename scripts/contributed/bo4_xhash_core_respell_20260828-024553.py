"""Respell cores from unquoted BO4 xhash names with target-game decorations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-source" / "tables" / "data" / "xhash"
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
TYPE_PREFIXES = ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_")


def names():
    found = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for value in lines:
            value = value.strip().lower().replace("\\", "/")
            if not value or value.startswith("hash_") or "_" not in value and "/" not in value:
                continue
            found.add(value)
    return found


def main():
    count = 0
    for value in sorted(names()):
        directory, slash, stem = value.rpartition("/")
        stem = stem.rsplit(".", 1)[0] if "." in stem else stem
        for prefix in TYPE_PREFIXES:
            if stem.startswith(prefix):
                stem = stem[len(prefix):]
                break
        if len(stem) < 4:
            continue
        for where in (directory, ""):
            lead = where + "/" if where else ""
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    print(lead + prefix + stem + suffix)
                    count += 1
    print(f"{count:,} streamed xhash core respellings", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
