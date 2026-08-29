"""Split a generated uncarried-beginnings plan into bounded prefix slices.

Run with: python contrib/uncarried_slice_plan_20260828.py --start 0 --count 26 --out plans/uncarried_slice_000_026.txt
Reads: an uncarried plan and its generated beginnings/stems lists.
Writes: a smaller beginnings list and confirm_plan plan; reusable for unattended-safe slices.
This is a reusable one-off utility; it does not generate candidate names itself.
"""
import argparse
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lines(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return [line.strip() for line in handle if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="plans/uncarried_latest_20260828.txt")
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = os.path.join(ROOT, args.source)
    source_base = os.path.splitext(source)[0]
    begins = lines(source_base + ".beginnings.txt")
    stems = os.path.relpath(source_base + ".stems.txt", ROOT).replace("\\", "/")
    selected = begins[args.start : args.start + args.count]
    if not selected:
        raise SystemExit("slice is empty")

    out = os.path.join(ROOT, args.out)
    base = os.path.splitext(out)[0]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    begin_path = base + ".beginnings.txt"
    with open(begin_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(selected) + "\n")

    begin_rel = os.path.relpath(begin_path, ROOT).replace("\\", "/")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("label: uncarried beginnings slice %d-%d\n" % (args.start, args.start + len(selected)))
        handle.write("begin: @%s\n" % begin_rel)
        handle.write("stem: @%s\n" % stems)
        handle.write("end: @data/suffixes.txt\n")
        handle.write("bare: no\nfold: yes\n")

    print("%d beginnings -> %s" % (len(selected), args.out))


if __name__ == "__main__":
    main()
