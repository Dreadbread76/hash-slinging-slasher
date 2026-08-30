"""Probe an uncarried sound-alias family head with sound endings."""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("head", help="uncarried alias family head, including trailing underscore")
    args = parser.parse_args()
    head = args.head.lower()
    known = {
        n.strip().lower().replace("\\", "/")
        for n in list(snapshot.table_names("fnv1a_soundbanks_aliases"))
        + list(snapshot.confirmed_names("sound_alias"))
        if n.strip()
    }
    family = sorted(n for n in known if n.startswith(head))
    stems = set()
    for name in family:
        rest = name[len(head):]
        tokens = rest.split("_")
        if len(rest) >= 4:
            stems.add(rest)
        for cut in range(1, len(tokens)):
            core = "_".join(tokens[:-cut])
            if len(core) >= 4:
                stems.add(core)
    endings_path = os.path.join(ROOT, "data", "sound.suffixes.txt")
    with open(endings_path, encoding="utf-8", errors="replace") as handle:
        endings = [line.strip().lower() for line in handle if line.strip()]
    candidates = {
        head + stem + ending
        for stem in stems
        for ending in endings
        if head + stem + ending not in known
    }
    print(f"{len(family):,} family seeds, {len(stems):,} stems, {len(candidates):,} candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)


if __name__ == "__main__":
    main()
