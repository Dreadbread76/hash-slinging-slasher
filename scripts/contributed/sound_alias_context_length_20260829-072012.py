"""Complete sound-alias names by a token whose surrounding context is already attested.

This is deliberately narrower than the generic token insertion/deletion method: it only uses
sound aliases, and an inserted token must have been observed between the exact same token prefix
and suffix in another known alias.  It therefore tests optional qualifiers in an alias family,
not a global sound vocabulary cross product.
"""
import collections
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = ("fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2")


def main():
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES)}
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names("sound_alias"))
    known.discard("")

    parsed = []
    for name in known:
        tokens = name.split("_")
        if 2 <= len(tokens) <= 14 and all(tokens):
            parsed.append((name, tokens))

    # For every exact context obtained by deleting one token, retain the tokens that real names
    # have between that context.  This makes insertion evidence local to both sides.
    between = collections.defaultdict(set)
    for _, tokens in parsed:
        for pos, token in enumerate(tokens):
            between[(tuple(tokens[:pos]), tuple(tokens[pos + 1:]))].add(token)

    out = set()
    for name, tokens in parsed:
        # The deletion half asks only whether a shorter, already-framed alias exists.
        for pos in range(len(tokens)):
            candidate = "_".join(tokens[:pos] + tokens[pos + 1:])
            if candidate and candidate not in known:
                out.add(candidate)

        # Reinsert an attested token for every context this name can expose.
        for pos in range(1, len(tokens)):
            context = (tuple(tokens[:pos]), tuple(tokens[pos:]))
            for token in between.get(context, ()):
                candidate = "_".join(tokens[:pos] + [token] + tokens[pos:])
                if candidate not in known:
                    out.add(candidate)

    for candidate in sorted(out):
        print(candidate)
    print("sound alias context length: %d known names, %d candidates" % (len(known), len(out)), file=sys.stderr)


if __name__ == "__main__":
    main()
