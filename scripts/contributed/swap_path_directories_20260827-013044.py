"""Swap the first two directory components of known non-sound asset paths."""
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
 names=set(snapshot.table_names(*TABLES)); names.update(snapshot.confirmed_names()); out=set()
 for n in names:
  n=n.strip().lower().replace("\\","/"); p=n.split("/")
  if len(p)<3 or any("." in x for x in p): continue
  p[0],p[1]=p[1],p[0]; out.add("/".join(p))
 for n in sorted(out): print(n)
 print(f"{len(names)} seeds, {len(out)} candidates",file=sys.stderr)
if __name__=="__main__": main()
