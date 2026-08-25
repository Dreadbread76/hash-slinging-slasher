"""Write a typed borrowed-ending plan over a disjoint ending rank band.

    python contrib/v2_typed_borrowed_endings_range.py --kind xanim --skip-ends 8000 \
        --ends 8000 --write-plan plans/v2_xanim_ends_8001_16000.txt

This is `typed_borrowed_endings.py` aimed at `_v2` typed source rows, with a rank slice on the
borrowed endings so a follow-up pass does not spend half its candidates rerunning the previous
band.
"""
import argparse
import collections
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))

from typed_cross import TYPES, cores, decorations, ours


def external_by_type(path):
    external = collections.defaultdict(set)
    with open(os.path.join(_root, path), encoding="utf-8", errors="replace") as handle:
        for line in handle:
            kind, _, name = line.partition(",")
            kind = kind.strip().lower()
            name = name.strip().strip('"').replace("\\", "/").lower()
            if name and kind in TYPES:
                external[kind].add(name)
    return external


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", default=os.path.join("borrowed", "v2_typed.txt"))
    parser.add_argument("--kind", default="xanim", choices=sorted(TYPES))
    parser.add_argument("--begins", type=int, default=1500)
    parser.add_argument("--ends", type=int, default=8000)
    parser.add_argument("--skip-ends", type=int, default=0)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--strip-depth", type=int, default=3)
    parser.add_argument("--strip-begins", type=int, default=250)
    parser.add_argument("--strip-ends", type=int, default=1200)
    parser.add_argument("--write-plan", required=True)
    options = parser.parse_args(argv)

    external = external_by_type(options.source)
    theirs = external.get(options.kind)
    if not theirs:
        raise SystemExit("%s has no %s rows" % (options.source, options.kind))

    mine = ours(options.kind, TYPES[options.kind])
    our_heads, our_tails = decorations(mine, options.depth, options.begins, options.ends)

    strip_h, strip_t = decorations(
        mine, options.strip_depth, options.strip_begins, options.strip_ends
    )
    stems = sorted(cores(mine, strip_h, strip_t))

    _, their_tails = decorations(theirs, options.depth, options.begins, 200000)
    carried = set(our_tails)
    borrowed_all = [tail for tail in their_tails if tail not in carried]
    borrowed = borrowed_all[options.skip_ends : options.skip_ends + options.ends]

    plan_path = os.path.join(_root, options.write_plan)
    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)

    for suffix, rows in (("begins", our_heads), ("stems", stems), ("ends", borrowed)):
        with open("%s.%s.txt" % (base, suffix), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(rows) + "\n")

    def rel(path):
        return os.path.relpath(path, _root).replace("\\", "/")

    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/v2_typed_borrowed_endings_range.py. Regenerate rather than editing.\n"
            "#\n"
            "# OUR %s cores and beginnings, under `_v2` %s endings ranked %d-%d after removing\n"
            "# endings our corpus already carries. This is disjoint from lower ending bands.\n"
            "\n"
            "label: _v2 %s borrowed endings, ranks %d-%d\n"
            "begin: @%s\n"
            "stem:  @%s\n"
            "end:   @%s\n"
            "bare:  no\n"
            % (
                options.kind,
                options.kind,
                options.skip_ends + 1,
                options.skip_ends + len(borrowed),
                options.kind,
                options.skip_ends + 1,
                options.skip_ends + len(borrowed),
                rel(base + ".begins.txt"),
                rel(base + ".stems.txt"),
                rel(base + ".ends.txt"),
            )
        )

    print(
        "%s: %s cores x %s begins x %s endings, ranks %s-%s -> %s candidates"
        % (
            options.kind,
            format(len(stems), ","),
            format(len(our_heads), ","),
            format(len(borrowed), ","),
            format(options.skip_ends + 1, ","),
            format(options.skip_ends + len(borrowed), ","),
            format(len(stems) * len(our_heads) * len(borrowed), ","),
        ),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
