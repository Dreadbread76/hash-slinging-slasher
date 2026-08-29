"""The beginnings `derive_lists.py` measures and its ceiling then throws away.

    python contrib/ceiling_dropped_begins.py --sound            list them (sound lists)
    python contrib/ceiling_dropped_begins.py --sound --plan plans/ceiling_sound.txt
    python contrib/ceiling_dropped_begins.py --general --plan plans/ceiling_general.txt

## The measurement this comes from

`reach.py` puts `xsounds` at **100% reached and 10.7% named**: the ending list can express these
names and the beginning list almost never can. That reads like a stale list wanting a re-measure.
It is not, and `derive_lists.py` says so in its own summary:

    sound.prefixes.txt: 839 measured, 14 carried, 153 past the ceiling of 700 dropped
    the ceiling cut 153 measured beginnings, the largest being vox/scripted/sims/ (454 names)

The measurement already finds the vocabulary; the **cap discards it**. So re-measuring cannot
help -- it discards a different 153, which is the displacement METHODS records for the general
lists (55 names, then 294, then 51, on a corpus two and a half times larger).

**A plan has no cap.** Putting the discarded beginnings in front of the engine reaches names the
general search cannot express at all, however long it runs. That is the whole method, and it is
why this is a plan rather than a list update: nothing shared changes, and no fingerprint moves.

Measured 2026-08-29, Cold War: 153 beginnings x 1,985,997 all-boundary sound cores x 2,890 sound
endings, 884 billion candidates, **9 names** -- and `derive_closure.py` turned those 9 seeds into
**18 more**. The 153 are real Cold War sound paths the cap cannot hold: `bik_execution_` (which
`reach.py` separately reports as heading 136 names with no cut carried),
`amb/cp_rus_amerika/control_room/emt_`, `cp/level/cp_nam_prisoner/bridge/evt_`.

## Why it borrows the lists and puts them back

There is no way to ask `derive_lists` for its measurement without letting it write, so this lifts
the ceiling, lets it write, takes the result and **restores the four committed lists from a backup
in a `finally`**. Nothing under `data/` is left changed, deliberately: those lists are shared
state, and moving them moves every contributor's fingerprint for no gain in reach.
"""

import argparse
import os
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
while ROOT != ROOT.parent and not (ROOT / "scripts" / "snapshot.py").is_file():
    ROOT = ROOT.parent

LISTS = ["prefixes.txt", "suffixes.txt", "sound.prefixes.txt", "sound.suffixes.txt"]
LIFTED = 100000


def measured_uncapped():
    """Run derive_lists with no ceiling, and put the committed lists back afterwards."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import derive_lists

    backup = tempfile.mkdtemp(prefix="lists-")
    for name in LISTS:
        source = ROOT / "data" / name
        if source.exists():
            shutil.copy(source, os.path.join(backup, name))

    ceiling, share = derive_lists.MOST_PREFIXES, derive_lists.CONFIRMED_PREFIX_SHARE
    try:
        derive_lists.MOST_PREFIXES = LIFTED
        derive_lists.CONFIRMED_PREFIX_SHARE = LIFTED
        try:
            derive_lists.main()
        except SystemExit:
            pass
        return {name: (ROOT / "data" / name).read_text(encoding="utf-8").split() for name in LISTS}
    finally:
        derive_lists.MOST_PREFIXES, derive_lists.CONFIRMED_PREFIX_SHARE = ceiling, share
        for name in LISTS:                      # the committed lists, back exactly as they were
            kept = os.path.join(backup, name)
            if os.path.exists(kept):
                shutil.copy(kept, ROOT / "data" / name)
        shutil.rmtree(backup, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sound", action="store_true")
    group.add_argument("--general", action="store_true")
    parser.add_argument("--plan", help="write a plan here instead of listing the beginnings")
    # Beside the plan, not in `contrib/`: `submit` carries everything in `contrib/` into the
    # pull request, so a generated list left there is sent as though it were a generator and
    # the tender holds the submission for a human. It happened twice on 2026-08-29. `plans/`
    # is gitignored and is where the thing this writes belongs.
    parser.add_argument("--out", default="plans/ceiling_dropped_begins.txt",
                        help="where the plan's begin list is written")
    args = parser.parse_args()

    which = "sound.prefixes.txt" if args.sound else "prefixes.txt"
    uncapped = measured_uncapped()[which]
    carried = set((ROOT / "data" / which).read_text(encoding="utf-8").split())
    dropped = [b for b in uncapped if b not in carried]

    print("%d measured uncapped, %d carried, %d dropped by the ceiling"
          % (len(uncapped), len(carried), len(dropped)), file=sys.stderr)

    if not args.plan:
        for beginning in dropped:
            print(beginning)
        return

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(dropped) + "\n", encoding="utf-8", newline="\n")

    stem = "borrowed/ab_sound_cores.txt" if args.sound else "borrowed/ab_cores.txt"
    end = "data/sound.suffixes.txt" if args.sound else "data/suffixes.txt"
    kind = "sound" if args.sound else "general"

    plan = pathlib.Path(ROOT / args.plan)
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(
        "label: %s beginnings the %d ceiling drops\n"
        "begin: @%s\n"
        "stem:  @%s\n"
        "end:   @%s\n" % (kind, LIFTED and 700, args.out, stem, end),
        encoding="utf-8", newline="\n")
    print("wrote %s and %s" % (args.plan, args.out), file=sys.stderr)


if __name__ == "__main__":
    main()
