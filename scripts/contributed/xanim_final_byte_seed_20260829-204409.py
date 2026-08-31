"""Try printable final-byte substitutions using only known xanim names as seeds."""
import os
import string
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def main():
    names = set(snapshot.table_names("fnv1a_xanims"))
    names.update(snapshot.confirmed_names("xanim"))
    alphabet = string.ascii_lowercase + string.digits + "_-"
    out = set()
    for value in names:
        value = value.strip().lower().replace("\\", "/")
        if len(value) < 2:
            continue
        for char in alphabet:
            candidate = value[:-1] + char
            if candidate != value:
                out.add(candidate)
    for candidate in sorted(out):
        print(candidate)
    print(f"{len(names):,} xanim seeds -> {len(out):,} final-byte candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
