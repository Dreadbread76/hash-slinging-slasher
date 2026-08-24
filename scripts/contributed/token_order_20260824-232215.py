"""token_order -- the sibling that is the same words in the other order.

METHODS.md listed this under "Candidates worth building" with the check that
decides it: *do any permutations of confirmed names already appear in the
tables? If none do, the convention is stable and this finds nothing.*

Measured 2026-08-25 by `contrib/measure_token_order.py`:

    confirmed corpus   57,066 names   300,906 transpositions   39 land on a known name
    published corpus  120,000 names   609,779 transpositions   80 land on a known name

i.e. **1 per ~7,700**, and the two corpora agree. So the naming does *not* fix
token order -- both spellings genuinely ship -- and every known name is a seed
for a sibling nothing in the registry can currently emit:

  * the general search composes `beginning + stem + ending`, so it can replace a
    head or a tail but never reorder a middle with both sides intact;
  * `slotswap` (method 10) substitutes a middle token but preserves its slot;
  * `confirm_variants` moves only numbers, and only in place;
  * `token_edits` inserts and deletes, never transposes.

**Reaches** pairs like these, all real, all already in the tables:

    mc/t8_usa_snow_flat_02          <-> mc/t8_snow_usa_flat_02
    wc/t7_concrete_worn_painted_white <-> wc/t7_concrete_painted_worn_white
    i_c_t9_tape_duct_01_g           <-> i_c_t9_duct_tape_01_g
    mc/mkg_fishing_net_01           <-> mc/mkg_net_fishing_01

**Spent by** the corpus it is run over. Each name yields about five candidates,
so the whole vocabulary is only single-digit millions of candidates -- cheap
enough to re-run after any pass that grows the corpus (`derive_closure.py`).
Once every name's transpositions have been tested against a fixed unnamed set,
re-running finds nothing until new names land.

This is an *edit*, not a cross product, so it prints names for `confirm_list`
rather than describing a plan -- see `src/bin/confirm_plan.rs` on that split.

    python contrib/token_order.py | bin\windows\confirm_list.exe - \
        --label "token order transpositions" --script contrib/token_order.py
"""
import os, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# BO4/BOCW tables only. The _v2 tables are MWII/MWIII/BO6/BO7/WZM under the IW
# offset and hashing their names against these games is measured dead.
PUBLISHED = ["fnv1a_xmaterials.csv", "fnv1a_ximages.csv",
             "fnv1a_xmodels.csv", "fnv1a_xanims.csv"]

# Seed from the five wanted types only. streamkey/xmodelmesh/localizeentry are
# machine-generated (CLAUDE.md §5) and would bury the real candidates.
SEED_POOLS = ("image", "material", "xmodel", "xanim")


def load_known():
    known = set()
    for fn in PUBLISHED:
        p = os.path.join(REPO, "cod-name-db", "csv", fn)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                c = line.find(",")
                if c >= 0:
                    known.add(line[c + 1:])
    # Both games seed each other: Cold War carries a great deal of Black Ops 4's
    # content, and a name real in one is evidence about spelling in the other.
    for p in glob.glob(os.path.join(REPO, "findings", "*", "*.txt")):
        if os.path.splitext(os.path.basename(p))[0] not in SEED_POOLS:
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\r\n")
                if not line:
                    continue
                c = line.find(",")
                known.add(line[c + 1:] if c >= 0 else line)
    return known


def transpositions(name):
    """Every adjacent MIDDLE-token transposition of `name`.

    parts[0] carries the directory and type code (`mc/mtl`) and parts[-1] is the
    channel or variant suffix (`_c`, `_dead`). Both ends are already reachable by
    begin/end composition, so only the middle is new ground.
    """
    parts = name.split("_")
    if len(parts) < 4:
        return
    for i in range(1, len(parts) - 2):
        a, b = parts[i], parts[i + 1]
        if a == b:
            continue
        yield "_".join(parts[:i] + [b, a] + parts[i + 2:])


def main():
    known = load_known()
    emitted = set()
    out = sys.stdout
    n = 0
    for name in known:
        for cand in transpositions(name):
            # A transposition that is itself already a known name is already
            # named -- a hit on one is not a find. Drop them here so the
            # candidate count means what it says.
            if cand in known or cand in emitted:
                continue
            emitted.add(cand)
            out.write(cand)
            out.write("\n")
            n += 1
    sys.stderr.write("token_order: %d seed names -> %d distinct new candidates\n"
                     % (len(known), n))


if __name__ == "__main__":
    main()
