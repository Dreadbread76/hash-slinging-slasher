"""Cross measured uncarried prefixes with basename cores from an external source dump."""
import argparse
import collections
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

EXTENSIONS = {".gsc", ".csc", ".cfg", ".csv", ".ddl", ".gdb", ".graph", ".raw", ".vision", ".txt", ".ai_htn"}
TABLES = ("fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages", "fnv1a_ximages_v2", "fnv1a_xmodels", "fnv1a_xanims", "fnv1a_xanims_v2")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--top", type=int, default=200)
    ap.add_argument("--cores", type=int, default=10000)
    ap.add_argument("--size", action="store_true")
    args = ap.parse_args()
    carried = {x.strip() for x in (ROOT / "data" / "prefixes.txt").read_text().splitlines() if x.strip()}
    counts = collections.Counter()
    for name in snapshot.table_names(*TABLES):
        name = name.lower().replace("\\", "/")
        for i, ch in enumerate(name):
            if ch in "_/" and i < 40:
                counts[name[:i + 1]] += 1
    begins = [b for b, _ in sorted(((b, n) for b, n in counts.items() if b not in carried), key=lambda x: (-x[1], x[0]))[:args.top]]
    cores = set()
    root = Path(args.root)
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        stem = path.stem.lower()
        if "_" in stem and len(stem) >= 5:
            cores.add(stem)
    cores = sorted(cores)[:args.cores]
    candidates = {begin + core for begin in begins for core in cores}
    print(f"{len(begins)} uncarried prefixes x {len(cores)} source basename cores -> {len(candidates)} candidates", file=sys.stderr)
    if not args.size:
        print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
