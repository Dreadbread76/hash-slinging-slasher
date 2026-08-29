"""Rotate all underscore-separated tokens left by one on known non-sound names."""
import os,sys
_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot
TABLES=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
def main():
 names=set(snapshot.table_names(*TABLES)); names.update(snapshot.confirmed_names())
 out=set()
 for n in names:
  n=n.strip().lower().replace("\\","/"); d,b=n.rsplit("/",1) if "/" in n else ("",n)
  if "." in b or b.count("_")<2: continue
  p=b.split("_"); r="_".join(p[1:]+p[:1]); out.add((d+"/" if d else "")+r)
 for n in sorted(out): print(n)
 print(f"{len(names)} seeds, {len(out)} candidates",file=sys.stderr)
if __name__=="__main__": main()
