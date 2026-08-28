"""Search the disjoint second slice of the measured material-to-xmodel seam."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seams

BEGINNINGS = ("attach_", "mtl_", "i_", "xmodel_", "mc/", "wc/", "clt/", "splm/", "vd/", "mcs_")
ENDINGS = ("_view", "_world", "_proxy", "_c", "_n", "_g", "_o", "_m", "_s", "_r")


def main():
    material = seams.load("material")
    xmodel = seams.load("xmodel")
    source = seams.cores(material, dict(seams.REDUCTIONS)["no head"])
    target = seams.cores(xmodel, dict(seams.REDUCTIONS)["no directory"])
    stems = sorted(source - target)[6000:12000]
    count = 0
    for beginning in BEGINNINGS:
        for stem in stems:
            for ending in ENDINGS:
                print(beginning + stem + ending)
                count += 1
    print(f"{count:,} streamed material-to-xmodel seam slice-2 candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
