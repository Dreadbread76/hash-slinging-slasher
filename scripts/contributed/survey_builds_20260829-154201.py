"""What every Call of Duty install on this machine is, and what it would cost to read.

    python contrib/survey_builds.py            every install, its containers and their magic
    python contrib/survey_builds.py --probe    also test whether the payload is readable

METHODS *The other builds on the disk* measured five sources and left the impression that the
rest were simply unvisited. They are not unvisited, they are **encrypted**, and this says so per
install rather than leaving it to be rediscovered.

A fast file's first eight bytes name the engine and the packing:

    IWffu100   Infinity Ward, "uncompressed"   -- the flag is about the container, not the payload
    IWff0100   Infinity Ward, compressed
    TAff0100   Treyarch T6 (Black Ops II), followed by the `PHEEBs71` marker -- Salsa20
    TAff0000   Treyarch T7 (Black Ops III)     -- what `harvest_bo3.py` already reads

**`IWffu100` does not mean plaintext.** That is the trap this script exists to close: the name
says uncompressed and the payload is still packed, so a scan finds 10-36% printable bytes and
strings like `XK_gsO` that look like names to a loose filter and are noise. `--probe` measures the
printable share and tries a zlib stream at every offset in the header, so the answer is a number
rather than an assumption.
"""

import argparse
import collections
import glob
import os
import re
import zlib

ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\common",
    r"D:\Steam\steamapps\common",
    r"D:\SteamLibrary\steamapps\common",
    r"D:\Battlenet",
]
NAMEISH = re.compile(rb"[A-Za-z0-9_./\-]{6,120}")


def probe(path):
    """(printable share of the first 200 KB, whether a zlib stream starts in the header)."""
    with open(path, "rb") as handle:
        raw = handle.read(4_000_000)
    body = raw[0x0C:]
    sample = body[:200_000]
    share = 100.0 * sum(1 for c in sample if 32 <= c < 127) / max(len(sample), 1)
    for offset in range(8, 64):
        try:
            out = zlib.decompressobj().decompress(raw[offset:], 2_000_000)
            if len(out) > 100_000:
                return share, True
        except Exception:
            pass
    return share, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true", help="also test whether payloads read")
    args = parser.parse_args()

    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if "call of duty" not in name.lower():
                continue
            folder = os.path.join(root, name)
            files = glob.glob(os.path.join(folder, "**", "*.ff"), recursive=True)
            if not files:
                other = collections.Counter(
                    os.path.splitext(f)[1].lower()
                    for f in glob.glob(os.path.join(folder, "**", "*.*"), recursive=True)[:4000])
                kinds = ", ".join(f"{e}x{c}" for e, c in other.most_common(3) if e)
                print(f"{name:44} no .ff   ({kinds})")
                continue

            magic = collections.Counter()
            for path in files:
                with open(path, "rb") as handle:
                    magic[handle.read(8)] += 1
            size = sum(os.path.getsize(f) for f in files) / 1e9
            spell = ", ".join(f"{m.decode('latin-1')}x{c}" for m, c in magic.most_common(3))
            print(f"{name:44} {len(files):4d} ff  {size:5.2f} GB  {spell}")

            if args.probe:
                for want in magic:
                    sample = next(f for f in files
                                  if open(f, "rb").read(8) == want)
                    share, inflates = probe(sample)
                    with open(sample, "rb") as handle:
                        head = handle.read(0x18)
                    marker = " PHEEBs71" if b"PHEEBs71" in head else ""
                    print(f"      {want.decode('latin-1')}{marker}: "
                          f"{share:.1f}% printable, zlib in header: {inflates}")


if __name__ == "__main__":
    main()
