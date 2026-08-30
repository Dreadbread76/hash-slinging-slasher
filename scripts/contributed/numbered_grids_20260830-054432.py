"""Compose missing cells in families with two or more numeric axes.

Unlike families.py, this keeps the complete numeric-token pattern and crosses values
already observed on each axis.  It never invents a number: every value came from a
confirmed name, and only unseen cells are emitted.
"""
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

NUMBER = re.compile(r"\d+")


def main():
    names = {
        n.strip().lower().replace(chr(92), "/")
        for kind in ("model", "material", "image", "anim", "sound file", "sound alias")
        for n in snapshot.confirmed_names(kind)
        if n.strip()
    }
    groups = collections.defaultdict(lambda: collections.defaultdict(set))
    for name in names:
        matches = list(NUMBER.finditer(name))
        if len(matches) < 2:
            continue
        template = NUMBER.sub("{}", name)
        values = [m.group(0) for m in matches]
        for axis, value in enumerate(values):
            groups[template][axis].add(value)

    candidates = set()
    for template, axes in groups.items():
        if len(axes) < 2 or any(len(values) < 2 for values in axes.values()):
            continue
        cells = {template.format(*values) for values in __import__("itertools").product(*(axes[i] for i in range(len(axes))))}
        candidates.update(cells - names)

    print("%d candidates from two-axis numeric families" % len(candidates), file=sys.stderr)
    sys.stdout.write("\n".join(sorted(candidates)))
    if candidates:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
