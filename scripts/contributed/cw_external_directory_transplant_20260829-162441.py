"""Put external mod basenames into Cold War's measured material directories.

The source-literal passes test external spellings at their original path depth.  This
separate method keeps their basenames but supplies the twelve Cold War material roots,
then tries the measured asset decorations.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
CORPORA = (ROOT / "borrowed" / "bo4-lucy-menu", ROOT / "borrowed" / "t8-atian-menu")
EXTENSIONS = {".gsc", ".csc", ".cfg", ".csv", ".ddl", ".gdb", ".graph", ".raw", ".vision", ".txt", ".json", ".md", ".yml", ".yaml"}
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./\\-]{5,159}")
PREFIXES = ("", "i_", "mtl_", "xmodel_", "xanim_")
SUFFIXES = ("", "_c", "_n", "_g", "_o", "_m", "_s", "_r")
DIRECTORIES = ("mc/", "wc/", "clt/", "splm/", "vd/", "mcs/", "ei/", "cltp/", "vdd/", "el/", "mcp/", "ec/")

def main():
    names = set()
    for corpus in CORPORA:
        if not corpus.is_dir():
            continue
        for path in corpus.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                try:
                    body = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for match in TOKEN.finditer(body):
                    value = match.group().lower().replace("\\", "/")
                    base = value.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                    if len(base) >= 4 and "_" in base and sum(c.isalpha() for c in base) >= 3:
                        names.add(base)
    # Keep this first probe bounded; the next band can be disjoint if it survives.
    names = set(sorted(names)[:3000])
    for base in sorted(names):
        for directory in DIRECTORIES:
            for prefix in PREFIXES:
                for suffix in SUFFIXES:
                    print(directory + prefix + base + suffix)
    print(f"{len(names):,} external basenames x 12 directories x 5 prefixes x 8 suffixes", file=sys.stderr)

if __name__ == "__main__":
    main()
