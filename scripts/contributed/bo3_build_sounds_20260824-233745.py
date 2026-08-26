"""Black Ops 3 sound-file names read out of the BUILD, not the SAB tables.

METHODS.md method 20 imports Black Ops 3 audio paths into Black Ops 4 spelling,
seeded from `bo3_sab.csv`. That corpus is the SAB tables -- 121,359 rows,
108,376 distinct basenames.

`borrowed/bo3_build.txt` is a different source for the same thing: a strings dump
of the Black Ops 3 build, in which 66,221 strings carry the sound-file shape
(a dotted encoding tail, `.sn100.pc.snd` and friends). Measured 2026-08-25:

    bo3_sab distinct basenames                    108,376
    bo3_build .snd basenames                       66,221
    of those, also in bo3_sab                      17,201
    of those, NOT in bo3_sab                    ** 49,020 **

So three quarters of what the build holds is outside the corpus method 20 ran,
and it is pointed at the largest unnamed ground in the project -- Black Ops 4
`sound_asset`, 70,707 unnamed of 79,263.

Why the two differ is worth writing down: the SAB tables are the *shipped* audio
packages, while the build's strings include names the build refers to whether or
not they survived into a package -- cut content, in-game-cinematic takes
(`05_sgen_igc_lobbyexit_v3`), versioned alternates (`_v1_16bit`, `_v3`). Those
are exactly the names a shipped table will not carry.

Emits a `type,name` manifest for `scripts/typed_cross.py --source`, which strips
each name's own measured tail to a core and crosses it with *our* directories and
*our* tails.

**The Black Ops 4 half of this pool does not fold.** CLAUDE.md §5: its ids are the
hash of the name with backslashes intact (8,385 of 8,385 reproduce unfolded, 0
folded), so the plan must carry `fold: no` or it matches nothing while looking
perfectly healthy.

    python contrib/bo3_build_sounds.py > plans/bo3snd.manifest.csv
    python scripts/typed_cross.py --source plans/bo3snd.manifest.csv \
        --write-plans plans/bo3snd
    # ensure `fold: no`, then
    bin\windows\confirm_plan.exe plans/bo3snd.sound_asset.txt --game BLKOPS04
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(REPO, "borrowed", "bo3_build.txt")
SAB = os.path.join(REPO, "borrowed", "bo3_sab.txt")

SHAPE = re.compile(r"^[a-z0-9_./\\$~+-]+$")


def basename(s):
    return s.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def main():
    used = set()
    if os.path.exists(SAB):
        with open(SAB, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                t = line.rstrip("\r\n").strip().lower()
                if t:
                    used.add(basename(t))

    seen = set()
    out = sys.stdout
    kept = overlap = 0
    with open(BUILD, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.rstrip("\r\n").strip().lower()
            if not (6 <= len(s) <= 120) or ".snd" not in s or not SHAPE.match(s):
                continue
            b = basename(s)
            if b in seen:
                continue
            seen.add(b)
            # Anything method 20 already had from the SAB tables is not new
            # ground; drop it here so the candidate count means what it says.
            if b in used:
                overlap += 1
                continue
            kept += 1
            out.write("sound_asset,")
            out.write(b)
            out.write("\n")
    sys.stderr.write("bo3_build_sounds: %d basenames new to the SAB corpus "
                     "(%d dropped as already used by method 20)\n" % (kept, overlap))


if __name__ == "__main__":
    main()
