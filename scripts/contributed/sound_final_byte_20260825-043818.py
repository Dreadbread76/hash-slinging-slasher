r"""The final-byte solve, pointed at the sound pools it has never been able to see.

    python contrib/sound_final_byte.py --game BLKOPS04 | bin/windows/confirm_list.exe - --no-fold \
        --label "sound final byte solved backwards" --script contrib/sound_final_byte.py

    python contrib/sound_final_byte.py --game BLKOPSCW | bin/windows/confirm_list.exe - \
        --label "sound final byte solved backwards" --script contrib/sound_final_byte.py

## The gap this exists for

`scripts/final_byte.py` is the best measured method in this project -- one name per 18 candidates,
against one per 394 for the next best -- and it is structurally blind to the largest unnamed
ground in either game. Two independent reasons, either of which alone would be enough:

**1. It never loads the sound-path corpus.** Its `TABLES` are the four general tables plus
`fnv1a_soundbanks_aliases`. The thirteen sound-*file* tables -- `fnv1a_xsounds.csv` and the twelve
per-language ones -- hold **861,019 names** between them and are not among them. So the solve has
essentially no prefixes for a sound path: the only ones it can offer are the ~165 `sound_asset`
names this repository has ever confirmed. It hunts those ids and cannot answer them.

**2. It folds.** `known_names()` ends `.replace("\\", "/")`, and its normalisation check rejects a
solved backslash for the same reason. Both are correct for every pool that folds -- and Black Ops
4's SAB sound names do not fold. Their ids are the hash of the literal backslashed path (8,385 of
8,385 reproduce unfolded, 0 folded), so a forward-slashed prefix hashes to something that is not
in the game, and every one of its 70,707 unnamed `sound_asset` ids is unreachable by the solve
however many prefixes it is given.

Verified here on 2026-08-25 against this repository's own confirmed Black Ops 4 `sound_asset`
names: of 104, **48 verify folded-or-plain and 56 verify only when the forward slashes `findings/`
records are put back to backslashes.** The findings tree stores a slash-normalised *display*
spelling; the hashed spelling is backslashed. Anything seeding from that file without converting
is seeding names the game does not hash.

## What it does

Exactly what `final_byte` does, with the corpus and the normalisation made game-correct:

  * prefixes come from all thirteen sound-file tables, the alias table, and every confirmed
    `sound_asset` / `sound_alias` name, in **the spelling the target game hashes**;
  * ids are the unnamed ones in `sound_asset` and `sound_alias` only, under both spellings of
    bit 63, exactly as `final_byte.unnamed_ids` does;
  * the solved byte is hashed back with that game's hash before it is believed. Under `--no-fold`
    a backslash is a legal solved byte and is kept -- it is a real character of a real name there,
    where under folding it is a spelling that cannot survive normalisation.

The solve is 256 dictionary lookups per unnamed id and builds no strings, so the whole thing is
seconds regardless of corpus size. See `scripts/final_byte.py` for the arithmetic.
"""
import argparse, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402

PRIME = 0x100000001B3
MASK = (1 << 64) - 1
PRIME_INVERSE = pow(PRIME, -1, 1 << 64)
TOP = 1 << 63
BS = chr(92)

LANGUAGES = ("americanspanish", "brazilianportugese", "chinese", "english", "french",
             "german", "italian", "japanese", "korean", "polish", "russian", "spanish")
SOUND_TABLES = (("fnv1a_xsounds", "fnv1a_soundbanks_aliases")
                + tuple("fnv1a_%s_xsounds" % lang for lang in LANGUAGES))
SOUND_POOLS = ("sound_asset", "sound_alias")


def corpus(nofold):
    """Every sound name known to be real, in the spelling the target game hashes.

    Black Ops 4 hashes the literal backslashed path, so forward slashes are put back; Cold War
    folds, so they are folded. Aliases carry no separator either way and are unaffected.
    """
    names = list(snapshot.table_names(*SOUND_TABLES))
    for pool in SOUND_POOLS:
        names += snapshot.confirmed_names(pool)

    out = set()
    for name in names:
        name = name.strip().lower()
        if not name:
            continue
        out.add(name.replace("/", BS) if nofold else name.replace(BS, "/"))
    return out


def claimed_ids(hasher):
    """Ids already answered by a merged submission or by anything confirmed on this machine.

    `snapshot.known_hashes()` reads the published tables and nothing else, so an id somebody
    recovered last night is still "unnamed" by that measure. Pointing a solve at those ids is not
    harmless: the corpus it solves *from* contains those same names, so the arithmetic closes on
    them over and over. Measured 2026-08-25 without this step: 1,910 names solved on Black Ops 4,
    every single one of them already claimed, and `confirm_list` hunted 21.
    """
    out = set()
    for folder in ("submissions", "findings"):
        for path in glob.glob(os.path.join(ROOT, folder, "**", "*.txt"), recursive=True):
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    key, _, name = line.partition(",")
                    name = (name or key).strip().lower()
                    if not name:
                        continue
                    # Both spellings: `findings/` stores sound paths slash-normalised while the
                    # game hashes Black Ops 4's with backslashes, so one of the two is the id.
                    out.add(hasher(name) & (TOP - 1))
                    out.add(hasher(name.replace("/", BS)) & (TOP - 1))
    return out


def sound_ids(game, hasher):
    """Unnamed `sound_asset` and `sound_alias` ids, under both spellings of the top bit."""
    chosen = None
    for path in snapshot.snapshots():
        shot = snapshot.read(path)
        if shot.game.lower() == game.lower():
            chosen = shot
            break
    if chosen is None:
        raise SystemExit("no snapshot for %s" % game)

    known = snapshot.known_hashes()
    ids = {value for value, pool in chosen.unnamed(known).items() if pool in SOUND_POOLS}
    before = len(ids)
    ids -= claimed_ids(hasher)
    sys.stderr.write(("unnamed sound ids: %s, of which %s are already claimed" + chr(10))
                     % ("{:,}".format(before), "{:,}".format(before - len(ids))))
    return chosen.game, ids | {value | TOP for value in ids}


def solve(names, ids, hasher):
    prefixes = {}
    for name in names:
        if len(name) >= 2:
            prefixes.setdefault(hasher(name[:-1]), name[:-1])

    found = {}
    for value in ids:
        scaled = (value * PRIME_INVERSE) & MASK
        for byte in range(256):
            prefix = prefixes.get(scaled ^ byte)
            if prefix is None:
                continue
            character = chr(byte)
            if not character.isprintable() or character.isspace():
                continue
            # Hashed back under the game's own rule before it is believed. Under --no-fold a
            # backslash survives and is a real character here; under folding it is not.
            name = prefix + character
            if hasher(name) == value:
                found[name] = value
    return found, len(prefixes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=None, help="BLKOPS04 or BLKOPSCW; default: what start chose")
    ap.add_argument("--targets", action="store_true", help="print id,name instead of names")
    args = ap.parse_args()

    game = args.game
    if not game:
        with open(os.path.join(ROOT, "state", "game.txt"), encoding="utf-8") as fh:
            game = fh.read().strip()

    nofold = game.lower() == "blkops04"
    hasher = snapshot.fnv1a_nofold if nofold else snapshot.fnv1a

    names = corpus(nofold)
    tag, ids = sound_ids(game, hasher)
    found, prefix_count = solve(names, ids, hasher)

    sys.stderr.write(
        "game: %s (%s)\nsound names loaded: %s   distinct prefixes: %s\n"
        "unnamed sound ids hunted: %s\nsolved: %s\n"
        % (tag, "unfolded" if nofold else "folded", "{:,}".format(len(names)),
           "{:,}".format(prefix_count), "{:,}".format(len(ids) // 2), "{:,}".format(len(found))))

    for name, value in sorted(found.items()):
        print("%016x,%s" % (value, name) if args.targets else name)


if __name__ == "__main__":
    main()
