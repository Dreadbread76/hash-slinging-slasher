"""Offer the bare basename of each known non-sound path as a candidate."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts")); import snapshot
TABLES=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
def main():
 names=set(snapshot.table_names(*TABLES)); names.update(snapshot.confirmed_names()); out=set()
 for n in names:
  n=n.strip().lower().replace("\\","/")
  if "/" in n and "." not in n: out.add(n.rsplit("/",1)[1])
 for n in sorted(out): print(n)
 print(f"{len(names)} seeds, {len(out)} candidates",file=sys.stderr)
if __name__=="__main__": main()
