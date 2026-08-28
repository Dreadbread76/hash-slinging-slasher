"""Material-only seam cores with common xmodel heads and mid-frequency tails."""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seams


def decorations(names):
    heads, tails = Counter(), Counter()
    for name in names:
        directory, bare = seams.split_directory(name)
        parts = bare.split("_")
        if len(parts) > 2:
            heads[directory + parts[0] + "_"] += 1
            tails["_" + parts[-1]] += 1
    return ([x for x, _ in heads.most_common(10)],
            [x for x, _ in tails.most_common(30)[10:]])


def main():
    material = seams.load("material")
    xmodel = seams.load("xmodel")
    stems = sorted(seams.cores(material, dict(seams.REDUCTIONS)["no head"]) -
                   seams.cores(xmodel, dict(seams.REDUCTIONS)["no directory"]))[:6000]
    beginnings, endings = decorations(xmodel)
    count = 0
    for beginning in beginnings:
        for stem in stems:
            for ending in endings:
                print(beginning + stem + ending)
                count += 1
    print(f"{count:,} streamed common-head mid-tail candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
