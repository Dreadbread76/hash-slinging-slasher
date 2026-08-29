"""Fill path-qualified voice aliases whose line tail is shared by multiple speakers."""
import collections
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = ("fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2",
          "fnv1a_xsounds", "fnv1a_xsounds_v2")


def main():
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES)}
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names("sound_alias"))
    known.discard("")

    speakers = set()
    tails = collections.Counter()
    for name in known:
        marker = "vox/scripted/"
        if not name.startswith(marker):
            continue
        rest = name[len(marker):]
        map_name, sep, rest = rest.partition("/")
        speaker, sep2, line = rest.partition("/")
        if not sep or not sep2 or not line.startswith("vox_"):
            continue
        # The first line token is speaker/record-specific; the remaining suffix is the shared
        # event/encoding shape that can legitimately recur across path-qualified voices.
        line_tokens = line[len("vox_"):].split("_")
        tail = "_".join(line_tokens[1:]) if len(line_tokens) > 1 else ""
        if speaker and tail:
            speakers.add(map_name + "/" + speaker)
            tails[tail] += 1

    shared = {tail for tail, count in tails.items() if count > 1}
    out = []
    for speaker in sorted(speakers):
        prefix = "vox/scripted/" + speaker + "/vox_"
        out.extend(prefix + tail for tail in sorted(shared)
                   if prefix + tail not in known)
    for name in sorted(set(out)):
        print(name)
    print("path vox grid: %d speakers x %d shared line tails = %d unseen cells" %
          (len(speakers), len(shared), len(set(out))), file=sys.stderr)


if __name__ == "__main__":
    main()
