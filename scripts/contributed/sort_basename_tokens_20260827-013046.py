"""Alphabetically sort underscore-separated basename tokens of known non-sound names."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts")); import snapshot
TABLES=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
def main():
 names=set(snapshot.table_names(*TABLES)); names.update(snapshot.confirmed_names()); out=set()
 for n in names:
  n=n.strip().lower().replace("\\","/"); d,b=n.rsplit("/",1) if "/" in n else ("",n)
  if "." in b or b.count("_")<2: continue
  out.add((d+"/" if d else "")+"_".join(sorted(b.split("_"))))
 for n in sorted(out): print(n)
 print(f"{len(names)} seeds, {len(out)} candidates",file=sys.stderr)
if __name__=="__main__": main()
