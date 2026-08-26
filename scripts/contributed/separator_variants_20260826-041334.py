"""Try observed underscore, dot and hyphen spelling variants between real tokens.

    python contrib/separator_variants.py --count
    python contrib/separator_variants.py | target\\release\\confirm_list.exe - --game BLKOPSCW \\
        --label "observed separator variants" --script contrib/separator_variants.py --anyway

This is a bounded spelling method.  It replaces a separator only if both separator spellings
between the same two token strings occur in the known corpus at least twice.  It therefore tests
an observed naming convention, not arbitrary punctuation substitutions.

Reads the five target tables and confirmed names through ``snapshot.py``.  Writes candidates to
stdout; ``--count`` only reports the size and known-name positive controls.  Reusable.
"""
import argparse
import collections
import os
import re
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import snapshot


TABLES = (
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
    "fnv1a_xanims",
    "fnv1a_xsounds",
    "fnv1a_soundbanks_aliases",
)
SEPARATOR = re.compile(r"([_.-])")


def corpus():
    names = set(snapshot.table_names(*TABLES))
    names.update(snapshot.confirmed_names())
    return {
        name.strip().lower().replace("\\\\", "/")
        for name in names
        if name.strip() and len(name) <= 160
    }


def pieces(name):
    """Return only editable separators, never a slash in a hashed directory."""
    directory, marker, base = name.rpartition("/")
    directory = directory + marker if marker else ""
    fields = SEPARATOR.split(base)
    return directory, fields


def alternatives(parsed):
    """{(left, right): separators} only where the convention repeats."""
    seen = collections.defaultdict(collections.Counter)
    for _, fields in parsed:
        for index in range(1, len(fields), 2):
            left, separator, right = fields[index - 1 : index + 2]
            if left and right:
                seen[(left, right)][separator] += 1
    return {
        pair: tuple(separator for separator, count in counts.items() if count >= 2)
        for pair, counts in seen.items()
        if len([count for count in counts.values() if count >= 2]) >= 2
    }


def make(parsed, known, choices):
    output = set()
    controls = 0
    for directory, fields in parsed:
        for index in range(1, len(fields), 2):
            left, current, right = fields[index - 1 : index + 2]
            for replacement in choices.get((left, right), ()):
                if replacement == current:
                    continue
                changed = list(fields)
                changed[index] = replacement
                candidate = directory + "".join(changed)
                if candidate in known:
                    controls += 1
                else:
                    output.add(candidate)
    return output, controls


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args(argv)

    known = corpus()
    parsed = [pieces(name) for name in known]
    choices = alternatives(parsed)
    output, controls = make(parsed, known, choices)
    print(
        "%s known names; %s observed separator relations; %s known-name controls; %s new candidates"
        % (format(len(known), ","), format(len(choices), ","), format(controls, ","), format(len(output), ",")),
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
