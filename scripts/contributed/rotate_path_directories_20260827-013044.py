"""Move the first path directory to the end on known non-sound asset paths."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts")); import snapshot
TABLES=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
def main():
 names=set(snapshot.table_names(*TABLES)); names.update(snapshot.confirmed_names()); out=set()
 for n in names:
  n=n.strip().lower().replace("\\","/"); p=n.split("/")
  if len(p)<3 or any("." in x for x in p): continue
  out.add("/".join(p[1:]+p[:1]))
 for n in sorted(out): print(n)
 print(f"{len(names)} seeds, {len(out)} candidates",file=sys.stderr)
if __name__=="__main__": main()
