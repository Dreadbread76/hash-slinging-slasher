r"""tails, with the endings MEASURED instead of enumerated.

`tails.py` is the best names-per-hour thing here, and it climbs badly. It cuts a
known name k characters short and tries every k-character string over a 37-letter
alphabet, so each rung costs 37x the last:

    k=3      50,653 endings     31.7 B candidates    21 seconds
    k=4   1,874,161 endings      1.34 T              ~13 minutes   (58 CW + 70 BO4, 2026-08-25)
    k=5  69,343,957 endings     48.07 T              ~7.8 hours

and at k=5 the collision figure stops being free: `confirm_plan --size` reports
**0.8392 names expected to match by chance**, against 0.0177 at k=4. CLAUDE.md §9
calls unconstrained character sweeps the last resort for exactly this reason.

Two measurements say the enumeration is the wrong half of that pass:

  * `contrib/measure_tail_alphabet.py` -- restricting the alphabet per position
    does **not** rescue it. The last five positions each use 32-34 characters of
    the 37, so a 99%-coverage alphabet is only 4.8x cheaper and loses ~5% of real
    tails. The alphabet is genuinely near-uniform; there is nothing to trim.

  * But the *combinations* are not. Of 69,343,957 possible 5-character strings,
    the naming only ever produces a small measured fraction of them -- real tails
    are `_01_c`, `s_02_`, `ial_n`, not arbitrary letter soup.

So this keeps `tails`' shape -- cut a known name k characters short, put a
different k-character ending on -- and takes the endings from **what names
actually end with** rather than from a cross product. That drops the cost by
two orders of magnitude, takes the collision figure back to nil, and lets k go
*deeper* than the enumerated ladder ever can.

It is deliberately a plan and not a printed list: cutting cores and crossing them
with endings is a cross product, and `src/bin/confirm_plan.rs` is blunt about
never printing one of those.

    python contrib/measured_tails.py --length 5
    bin\windows\confirm_plan.exe plans/mtails5.txt --size
"""
import argparse, os, glob, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]
GENERAL = ("image", "material", "xmodel", "xanim")


def load():
    names = set()
    for fn in PUBLISHED:
        p = os.path.join(REPO, "cod-name-db", "csv", fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    names.add(line[c + 1:])
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        if os.path.splitext(os.path.basename(p))[0] not in GENERAL:
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                c = line.find(",")
                names.add(line[c + 1:] if c >= 0 else line)
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=5,
                    help="how many characters to replace")
    ap.add_argument("--min-ending", type=int, default=1,
                    help="drop endings seen fewer than this many times")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    k = args.length

    names = [n for n in load() if len(n) > k + 3]
    sys.stderr.write("names usable at k=%d: %d\n" % (k, len(names)))

    endings = Counter()
    stems = set()
    for n in names:
        endings[n[-k:]] += 1
        stems.add(n[:-k])

    keep = [e for e, c in endings.most_common() if c >= args.min_ending]
    stems = sorted(stems)
    sys.stderr.write("distinct %d-character endings observed: %d (keeping %d)\n"
                     % (k, len(endings), len(keep)))

    out = args.out or os.path.join(REPO, "plans", "mtails%d" % k)

    def write(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(r + "\n")

    write(out + ".stems.txt", stems)
    write(out + ".ends.txt", keep)
    rel = os.path.basename(out)
    with open(out + ".txt", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Written by contrib/measured_tails.py --length %d\n#\n" % k)
        fh.write("# `tails` with the endings measured rather than enumerated: every\n")
        fh.write("# known name cut %d characters short, wearing every %d-character\n" % (k, k))
        fh.write("# ending any name is actually observed to end with.\n\n")
        fh.write("label: measured tails of length %d\n" % k)
        fh.write("stem:  @plans/%s.stems.txt\n" % rel)
        fh.write("end:   @plans/%s.ends.txt\n" % rel)
        # `bare: yes` is what lets a plan with no `begin` axis multiply out --
        # tails.py's own plan does the same. With `bare: no` and no beginnings
        # the product is zero and the plan silently sizes at 0 candidates.
        fh.write("bare:  yes\n")

    total = len(stems) * len(keep)
    enumerated = 37 ** k
    print("k=%d: %s stems x %s measured endings = %s candidates"
          % (k, "{:,}".format(len(stems)), "{:,}".format(len(keep)),
             "{:,}".format(total)))
    print("      enumerated tails.py would use %s endings -- %.0fx more"
          % ("{:,}".format(enumerated), enumerated / float(len(keep))))
    print("wrote %s.txt" % out)


if __name__ == "__main__":
    main()
