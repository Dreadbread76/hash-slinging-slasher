"""Fill evidenced two-axis map-prefix/mode grids around shared asset bodies.

    python contrib/map_prefix_mode_grid.py --measure
    python contrib/map_prefix_mode_grid.py | bin\\windows\\confirm_list.exe - \
        --label "map prefix and mode grid completion" \
        --script contrib/map_prefix_mode_grid.py

An ordinary token substitution can change `p9` or `zm` in isolation.  This reaches the missing
cell when the same body is already observed under multiple map-era prefixes *and* multiple game
modes, so both leading tokens must change together.  Only real `(pN, mode, body)` spellings from
the tables and confirmed findings supply an axis or a body.

Reads the six target tables and confirmed findings through scripts/snapshot.py.  Writes unseen,
evidenced cells to stdout; --measure reports the grid/control population without emitting them.
Reusable after new map-family names land.
"""
import argparse
import collections
import os
import re
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))

import snapshot

TABLES = (
    "fnv1a_ximages", "fnv1a_xmaterials", "fnv1a_xmodels", "fnv1a_xanims",
    "fnv1a_xsounds", "fnv1a_soundbanks_aliases",
)
FORM = re.compile(r"^(p[0-9]+)_(mp|zm|cp|sp|wz)_(.{4,})$")


def known_names():
    names = set()
    for table in TABLES:
        names.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for kind in ("image", "material", "xmodel", "xanim", "sound_asset", "sound_alias"):
        names.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind))
    return {name for name in names if name}


def grids(names):
    by_body = collections.defaultdict(set)
    for name in names:
        match = FORM.match(name)
        if match:
            by_body[match.group(3)].add((match.group(1), match.group(2)))
    return by_body


def missing_cells(by_body):
    for body, cells in by_body.items():
        prefixes = {prefix for prefix, _ in cells}
        modes = {mode for _, mode in cells}
        # A single-axis variation is precisely slotswap's territory.  At least three observed
        # cells over two values per axis establish a grid rather than two unrelated names.
        if len(prefixes) < 2 or len(modes) < 2 or len(cells) < 3:
            continue
        if len(prefixes) * len(modes) > 64:
            continue
        for prefix in prefixes:
            for mode in modes:
                if (prefix, mode) not in cells:
                    yield "%s_%s_%s" % (prefix, mode, body)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--measure", action="store_true")
    options = parser.parse_args(argv)
    names = known_names()
    by_body = grids(names)
    eligible = [cells for cells in by_body.values()
                if len({p for p, _ in cells}) >= 2 and len({m for _, m in cells}) >= 2 and len(cells) >= 3]
    candidates = set(missing_cells(by_body)) - names
    observed = sum(len(cells) for cells in eligible)
    print(
        "%s known names; %s map bodies; %s two-axis grids; %s observed grid cells; %s missing cells"
        % tuple(format(value, ",") for value in (
            len(names), len(by_body), len(eligible), observed, len(candidates)
        )),
        file=sys.stderr,
    )
    if not options.measure:
        sys.stdout.write("\n".join(sorted(candidates)))
        if candidates:
            sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
