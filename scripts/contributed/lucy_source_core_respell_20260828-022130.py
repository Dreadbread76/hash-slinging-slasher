"""Respell cores from the isolated BO4 Lucy menu source corpus."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "borrowed" / "bo4-lucy-menu"
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./\\-]{5,159}")
QUOTED = re.compile(r'\"([^\"]{6,160})\"|\'([^\']{6,160})\'')
EXTENSIONS = {".gsc", ".txt", ".md", ".csv", ".ps1", ".json", ".conf", ".yml", ".yaml"}
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
TYPE_PREFIXES = ("i_", "mtl_", "xmodel_", "xanim_", "mat_", "model_", "anim_")


def values():
    found = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            body = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        raw = [m.group() for m in TOKEN.finditer(body)]
        raw += [m.group(1) or m.group(2) for m in QUOTED.finditer(body)]
        for item in raw:
            item = item.strip().lower().replace("\\", "/")
            if ("_" in item or "/" in item) and sum(c.isalpha() for c in item) >= 3:
                found.add(item)
    return found


def main():
    candidates = set()
    for item in values():
        directory, slash, stem = item.rpartition("/")
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
                    candidates.add(lead + prefix + stem + suffix)
    for item in sorted(candidates):
        print(item)
    print(f"{len(candidates):,} Lucy external-core respellings", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
