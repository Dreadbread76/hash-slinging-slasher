"""Does every pool really normalise the same way? Test case and slash, per pool.

CLAUDE.md §6 states the rule: the name is **lower cased, and backslash folded to
forward slash**, then FNV-1a 64, compared at 63 bits. §5 then records the one
place that rule is wrong -- Black Ops 4 `sound_asset` ids are the hash of the
name with its backslashes INTACT (8,385 of 8,385 reproduce unfolded, 0 folded),
and until somebody found that, the largest pool in either game matched nothing
"while looking perfectly healthy".

That was one normalisation rule hiding one whole pool. This asks the obvious
next question nobody has: **is any pool hiding behind the OTHER half of the
rule -- the lower casing?** And is any other pool unfolded like BO4 sound?

The test is decisive and costs nothing, because we already hold the answer key:
`all_names/<game>/<type>.txt` is `id,name` for names whose ids are known. So for
every pool, hash its known names four ways and count which variant reproduces
the stored id:

    fold+lower   the documented rule
    fold only    case preserved
    lower only   backslashes intact  <- the BO4 sound_asset case
    neither

A pool where "fold+lower" scores 100% is confirmed normal. A pool where some
other variant wins is a pool whose ids nothing here can currently reach.

Read-only: reads name lists, prints a table, writes nothing.
"""
import os, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASIS = 0xCBF29CE484222325
PRIME = 0x100000001B3
MASK64 = (1 << 64) - 1
MASK63 = (1 << 63) - 1


def fnv1a(data):
    h = BASIS
    for b in data:
        h ^= b
        h = (h * PRIME) & MASK64
    return h


VARIANTS = (
    ("fold+lower", True, True),
    ("fold only", True, False),
    ("lower only", False, True),
    ("neither", False, False),
)


def hashed(name, fold, lower):
    s = name
    if fold:
        s = s.replace("\\", "/")
    if lower:
        s = s.lower()
    return fnv1a(s.encode("utf-8", "replace")) & MASK63


def main():
    print("%-10s %-13s %8s  %s" % ("game", "pool", "names", "which normalisation reproduces the id"))
    print("-" * 92)
    for gamedir in sorted(glob.glob(os.path.join(REPO, "all_names", "*"))):
        if not os.path.isdir(gamedir):
            continue
        game = os.path.basename(gamedir)
        for path in sorted(glob.glob(os.path.join(gamedir, "*.txt"))):
            pool = os.path.splitext(os.path.basename(path))[0]
            scores = {v[0]: 0 for v in VARIANTS}
            total = 0
            has_backslash = 0
            has_upper = 0
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.rstrip("\r\n")
                    if not line:
                        continue
                    c = line.find(",")
                    if c < 0:
                        continue
                    try:
                        want = int(line[:c], 16) & MASK63
                    except ValueError:
                        continue
                    name = line[c + 1:]
                    total += 1
                    if "\\" in name:
                        has_backslash += 1
                    if name != name.lower():
                        has_upper += 1
                    for label, fold, lower in VARIANTS:
                        if hashed(name, fold, lower) == want:
                            scores[label] += 1
            if not total:
                continue
            best = max(scores.items(), key=lambda kv: kv[1])
            detail = "  ".join("%s %5.1f%%" % (lab, 100.0 * scores[lab] / total)
                               for lab, _, _ in VARIANTS)
            flag = ""
            if best[1] < total:
                flag = "   <-- %d of %d unexplained" % (total - best[1], total)
            print("%-10s %-13s %8d  %s%s" % (game, pool, total, detail, flag))
            if has_backslash or has_upper:
                print("%-10s %-13s %8s  (%d names carry a backslash, %d carry upper case)"
                      % ("", "", "", has_backslash, has_upper))


if __name__ == "__main__":
    main()
