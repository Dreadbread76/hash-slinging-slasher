r"""Measured tails and measured heads, on the corpus the enumerated ladder actually uses.

    python contrib/measured_offsets.py --tail 8
    python contrib/measured_offsets.py --head 12
    bin\windows\confirm_plan.exe plans/mo_t8.txt --size

## What this supersedes and why

`contrib/measured_tails.py` (method 33) and `contrib/measured_heads.py` (method 34) both take
their stems and their vocabulary from **four published tables and the four general findings
files**:

    fnv1a_xmaterials, fnv1a_ximages, fnv1a_xmodels, fnv1a_xanims
    findings/*/{image,material,xmodel,xanim}.txt

`scripts/tails.py`, the enumerated method both of them are a fix to, uses those four tables
**plus `fnv1a_soundbanks_aliases` plus `snapshot.confirmed_names()` with no type filter** -- which
is every name anybody has confirmed or submitted, of every type, sound paths included.

So the two measured methods were run against a corpus narrower than the method they improve on.
That matters twice over, because both halves of a measured method come out of the corpus:

  * **stems.** Around 100,000 alias names and every confirmed sound path were simply not offered
    as stems, so no candidate was ever built on one.
  * **vocabulary.** An ending or an opening is kept because a real name was observed to use it.
    Aliases are a different shape from the general types -- bare underscore names, no directory,
    no channel code -- so their openings and endings are largely disjoint from the general ones,
    and the measured lists could not contain them at all.

This is the same class of mistake as the one METHODS records against `--head`, which measured its
alphabet off the end of the name it was replacing at the front: **a measured method is only as
good as what it measured, and nothing checks that.**

Both directions live here rather than in two files because they differ by one slice.
"""
import argparse, os, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import snapshot  # noqa: E402

# Exactly scripts/tails.py's TABLES. Kept as a literal rather than imported so that a change
# there is a visible difference here rather than a silent one.
TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
          "fnv1a_soundbanks_aliases")


LANGUAGES = ("americanspanish", "brazilianportugese", "chinese", "english", "french", "german",
             "italian", "japanese", "korean", "polish", "russian", "spanish")
SOUND_TABLES = (("fnv1a_xsounds", "fnv1a_soundbanks_aliases")
                + tuple("fnv1a_%s_xsounds" % lang for lang in LANGUAGES))
BS = chr(92)


def load_sound(nofold):
    """The sound corpus, in the spelling the target game hashes.

    Neither measured method has ever been given these 861,019 names: `TABLES` above is
    `scripts/tails.py`'s, and that does not carry the sound-file tables either. So the offset
    ladder -- the most productive thing measured here -- has never been pointed at the pool with
    70,707 unnamed ids in it.
    """
    names = set(snapshot.table_names(*SOUND_TABLES))
    for pool in ("sound_asset", "sound_alias"):
        names |= {n.strip() for n in snapshot.confirmed_names(pool) if n.strip()}
    out = set()
    for n in names:
        n = n.strip().lower()
        if n:
            out.add(n.replace("/", BS) if nofold else n.replace(BS, "/"))
    return out


def load(wide):
    names = set(snapshot.table_names(*TABLES))
    if wide:
        names |= {n.strip() for n in snapshot.confirmed_names() if n.strip()}
    return {n for n in names if n}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tail", type=int, help="replace this many characters at the end")
    g.add_argument("--head", type=int, help="replace this many characters at the front")
    ap.add_argument("--sound", choices=("fold", "nofold"), default=None,
                    help="measure and cut the SOUND corpus instead; nofold for Black Ops 4")
    ap.add_argument("--narrow", action="store_true",
                    help="tables only, no confirmed names -- for reproducing an older measurement")
    ap.add_argument("--min-seen", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    head = args.head is not None
    k = args.head if head else args.tail

    pool = load_sound(args.sound == "nofold") if args.sound else load(not args.narrow)
    names = [n for n in pool if len(n) > k + 3]
    sys.stderr.write("names usable at k=%d: %s\n" % (k, "{:,}".format(len(names))))

    vocab, stems = Counter(), set()
    for n in names:
        if head:
            vocab[n[:k]] += 1
            stems.add(n[k:])
        else:
            vocab[n[-k:]] += 1
            stems.add(n[:-k])

    keep = [v for v, c in vocab.most_common() if c >= args.min_seen]
    stems = sorted(stems)

    tag = ("h%d" if head else "t%d") % k
    if args.sound:
        tag = "snd_" + tag
    out = args.out or os.path.join(REPO, "plans", "mo_%s" % tag)

    def write(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(r + "\n")

    write(out + ".stems.txt", stems)
    write(out + ".vocab.txt", keep)
    rel = os.path.basename(out)
    with open(out + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by contrib/measured_offsets.py --%s %d\n#\n"
                 % ("head" if head else "tail", k))
        fh.write("# Every known name cut %d characters short at the %s, wearing every\n"
                 % (k, "front" if head else "end"))
        fh.write("# %d-character %s any name is observed to use, over the full corpus\n"
                 % (k, "opening" if head else "ending"))
        fh.write("# scripts/tails.py draws on -- aliases and confirmed sound names included.\n\n")
        fh.write("label: measured %s of length %d, wide corpus\n"
                 % ("heads" if head else "tails", k))
        if head:
            fh.write("begin: @plans/%s.vocab.txt\n" % rel)
            fh.write("stem:  @plans/%s.stems.txt\n" % rel)
        else:
            fh.write("stem:  @plans/%s.stems.txt\n" % rel)
            fh.write("end:   @plans/%s.vocab.txt\n" % rel)
            # See METHODS: replacing tails there is no `begin` axis, so `bare` supplies the only
            # opening column and the plan sizes at zero without it.
            fh.write("bare:  yes\n")

    print("%s k=%d: %s %s x %s stems = %s candidates"
          % ("heads" if head else "tails", k, "{:,}".format(len(keep)),
             "openings" if head else "endings", "{:,}".format(len(stems)),
             "{:,}".format(len(keep) * len(stems))))
    print("wrote %s.txt" % out)


if __name__ == "__main__":
    main()
