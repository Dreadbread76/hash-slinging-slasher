"""Swap final characters between each adjacent basename token pair."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts"))
import snapshot
tables=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
known=set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
for raw in sorted(known):
 n=raw.lower().replace('\\','/')
 if '/' not in n or '.' in n.rsplit('/',1)[-1]: continue
 d,b=n.rsplit('/',1); t=b.split('_')
 if len(t)<4 or any(not x for x in t): continue
 for i in range(len(t)-1):
  a,c=t[i],t[i+1]; out=list(t)
  out[i],out[i+1]=a[:-1]+c[-1],c[:-1]+a[-1]
  cand=d+'/'+'_'.join(out)
  if cand not in known: print(cand)
