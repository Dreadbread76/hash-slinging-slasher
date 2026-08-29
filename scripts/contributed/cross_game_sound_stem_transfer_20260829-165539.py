"""Transfer external BO4 SAB stems across the two games' measured sound tails."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
STEMS = ROOT / "contrib" / "blkops04_sound_asset_stems.txt"
SUFFIXES = ROOT / "data" / "sound.suffixes.txt"

def main():
    stems = {x.strip().lower().replace("/", "\\") for x in STEMS.read_text().splitlines() if x.strip()}
    suffixes = {x.strip().lower().replace("/", "\\") for x in SUFFIXES.read_text().splitlines() if x.strip()}
    for stem in sorted(stems):
        for suffix in sorted(suffixes):
            print(stem + suffix if suffix.startswith(".") or suffix.startswith("_") else stem + "_" + suffix)
    print(f"{len(stems):,} SAB stems x {len(suffixes):,} measured sound tails", file=sys.stderr)

if __name__ == "__main__":
    main()
