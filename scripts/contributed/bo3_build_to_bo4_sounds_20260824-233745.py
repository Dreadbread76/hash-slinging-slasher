r"""BO3 build sound names, worn in Black Ops 4 spelling. Writes a `confirm_plan` plan.

METHODS.md method 20 imports Black Ops 3 audio into Black Ops 4 from `bo3_sab.csv`.
This uses a *different* Black Ops 3 source for the same thing -- the strings in
`borrowed/bo3_build.txt` -- and measured 2026-08-25 three quarters of it is
outside the SAB corpus:

    bo3_sab distinct basenames                    108,376
    bo3_build .snd basenames                       66,221
    also in bo3_sab                                17,201
    NOT in bo3_sab                              ** 49,020 **

Aimed at the largest unnamed ground in the project: Black Ops 4 `sound_asset`,
70,707 unnamed of 79,263.

`scripts/typed_cross.py` will not do this one, for two reasons worth recording:

  * **Its beginnings come out in Cold War's spelling.** They are measured across
    our corpus and emerge as `amb/env/`, forward slashes, 0 of 250 carrying a
    backslash. Black Ops 4 sound ids are the hash of the name with backslashes
    INTACT and the plan must not fold, so every one of those beginnings would
    hash to something the game does not hold -- a clean zero, from a plan that
    looks perfectly healthy. This is exactly the trap CLAUDE.md §5 documents.

  * **Its generic stripping leaves tails inside the cores.** Sound names carry a
    dotted encoding tail, and stems came out as `00.ll100.pc.snd`, which crossed
    with an ending of `_01.ln75.pc.all.snd` spells a name with two tails.

So both sides are measured here directly: the cores have everything from the
first dot removed, and the directories and tails are measured on Black Ops 4's
OWN known sound_asset names -- recovered by hashing the sound tables unfolded and
keeping whatever lands on a Black Ops 4 sound_asset id.

    python contrib/bo3_build_to_bo4_sounds.py
    bin\windows\confirm_plan.exe plans/bo3build_bo4snd.txt --size
    bin\windows\confirm_plan.exe plans/bo3build_bo4snd.txt --game BLKOPS04
"""
import os, re, sys, glob
from collections import Counter

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

BUILD = os.path.join(_root, "borrowed", "bo3_build.txt")
SAB = os.path.join(_root, "borrowed", "bo3_sab.txt")
OUT = os.path.join(_root, "plans", "bo3build_bo4snd")

SHAPE = re.compile(r"^[a-z0-9_./\\$~+-]+$")

# How many of each to carry. Directories are the expensive axis and the long
# tail of them is one-name-deep, so they are ranked by how many known names sit
# under them; tails are few and all of them are carried.
MAX_DIRS = 400
MAX_TAILS = 40


def basename(s):
    return s.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def bo4_known_sound_names():
    """Black Ops 4 sound_asset names we already know, by hashing tables unfolded.

    Black Ops 4's sound ids are the hash of the name with its backslashes intact
    (CLAUDE.md §5: 8,385 of 8,385 reproduce unfolded, 0 folded), so `fnv1a_nofold`
    is the only function that will land on one.
    """
    snap = None
    for path in snapshot.snapshots():
        if "blkops04" in os.path.basename(path).lower():
            snap = snapshot.read(path)
            break
    if snap is None:
        raise SystemExit("no Black Ops 4 snapshot found")

    wanted = set()
    for asset_id, pool in snap.records:
        if snap.pool_name(pool) == "sound_asset":
            wanted.add(asset_id)
    sys.stderr.write("BLKOPS04 sound_asset ids in the snapshot: %d\n" % len(wanted))

    names = []
    folder = os.path.join(_root, "cod-name-db", "csv")
    for path in sorted(glob.glob(os.path.join(folder, "*xsounds*.csv"))):
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                _, _, name = line.partition(",")
                name = name.strip()
                if not name:
                    continue
                if snapshot.fnv1a_nofold(name) & snapshot.ID_MASK in wanted:
                    names.append(name)
    # Whatever this project has already confirmed for the pool counts too.
    for p in glob.glob(os.path.join(_root, "findings", "blkops04", "sound_asset.txt")):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    names.append(line[c + 1:])
    return names


def main():
    known = bo4_known_sound_names()
    sys.stderr.write("known BLKOPS04 sound_asset names recovered: %d\n" % len(known))
    if len(known) < 100:
        raise SystemExit("too few known names to measure a convention from")

    dirs, tails = Counter(), Counter()
    for n in known:
        base = basename(n)
        head = n[:len(n) - len(base)]          # keeps the trailing separator
        if head:
            dirs[head] += 1
        dot = base.find(".")
        if dot > 0:
            tails["." + base[dot + 1:]] += 1

    top_dirs = [d for d, _ in dirs.most_common(MAX_DIRS)]
    top_tails = [t for t, _ in tails.most_common(MAX_TAILS)]
    sys.stderr.write("measured %d directories (carrying %d), %d tails (carrying %d)\n"
                     % (len(dirs), len(top_dirs), len(tails), len(top_tails)))

    used = set()
    if os.path.exists(SAB):
        with open(SAB, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                t = line.rstrip("\r\n").strip().lower()
                if t:
                    used.add(basename(t))

    cores, seen = [], set()
    overlap = 0
    with open(BUILD, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.rstrip("\r\n").strip().lower()
            if not (6 <= len(s) <= 120) or ".snd" not in s or not SHAPE.match(s):
                continue
            b = basename(s)
            if b in used:
                overlap += 1
                continue
            dot = b.find(".")
            core = b[:dot] if dot > 0 else b
            if not core or core in seen:
                continue
            seen.add(core)
            cores.append(core)
    sys.stderr.write("cores from the build: %d (%d dropped as already in the SAB corpus)\n"
                     % (len(cores), overlap))

    def write(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(r + "\n")

    write(OUT + ".begins.txt", top_dirs)
    write(OUT + ".stems.txt", cores)
    write(OUT + ".ends.txt", top_tails)

    with open(OUT + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by contrib/bo3_build_to_bo4_sounds.py.\n")
        fh.write("#\n")
        fh.write("# Black Ops 3 build sound cores, under Black Ops 4's own measured\n")
        fh.write("# directories and encoding tails.\n")
        fh.write("#\n")
        fh.write("# fold: no is not optional. Black Ops 4 sound ids are the hash of the\n")
        fh.write("# name with its backslashes intact; folded, this plan matches nothing\n")
        fh.write("# while looking perfectly healthy. CLAUDE.md §5.\n")
        fh.write("\n")
        fh.write("label: bo3 build sound cores, black ops 4 spelling\n")
        fh.write("begin: @plans/bo3build_bo4snd.begins.txt\n")
        fh.write("stem:  @plans/bo3build_bo4snd.stems.txt\n")
        fh.write("end:   @plans/bo3build_bo4snd.ends.txt\n")
        fh.write("bare:  no\n")
        fh.write("fold:  no\n")
    print("wrote %s.txt -- %d x %d x %d = %d candidates"
          % (OUT, len(top_dirs), len(cores), len(top_tails),
             len(top_dirs) * len(cores) * len(top_tails)))


if __name__ == "__main__":
    main()
