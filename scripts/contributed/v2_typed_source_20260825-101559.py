"""Write the cod-name-db `_v2` tables as a typed external corpus.

    python contrib/v2_typed_source.py --out borrowed/v2_typed.txt

`scripts/typed_cross.py` and its split variants expect `type,name` rows. The newer-title tables
already carry their type by table, but not as a manifest file, so this bridges that format without
inventing any names.
"""
import argparse
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))

import snapshot

TABLES = {
    "image": "fnv1a_ximages_v2",
    "material": "fnv1a_xmaterials_v2",
    "xanim": "fnv1a_xanims_v2",
    "sound_alias": "fnv1a_soundbanks_aliases_v2",
    "sound_asset": "fnv1a_xsounds_v2",
}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=os.path.join("borrowed", "v2_typed.txt"))
    options = parser.parse_args(argv)

    rows = set()
    for kind, table in TABLES.items():
        for raw in snapshot.table_names(table):
            name = raw.strip().lower().replace("\\", "/")
            if name:
                rows.add((kind, name))

    os.makedirs(os.path.dirname(os.path.join(_root, options.out)), exist_ok=True)
    with open(os.path.join(_root, options.out), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join("%s,%s" % row for row in sorted(rows)) + "\n")

    print("%s typed name(s) -> %s" % (format(len(rows), ","), options.out), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
