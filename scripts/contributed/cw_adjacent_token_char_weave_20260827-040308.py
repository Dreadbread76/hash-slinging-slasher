"""Weave characters of each adjacent token pair into one token."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import snapshot
tables=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
known=set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
for raw in sorted(known):
 n=raw.lower().replace('\\','/')
 if '/' not in n or '.' in n.rsplit('/',1)[-1]: continue
 d,b=n.rsplit('/',1); t=b.split('_')
 if len(t)<4 or any(not x for x in t): continue
 for i in range(len(t)-1):
  a,c=t[i],t[i+1]; w=''.join(x for pair in zip(a,c) for x in pair)+a[len(c):]+c[len(a):]
  out=t[:i]+[w]+t[i+2:]; cand=d+'/'+ '_'.join(out)
  if cand not in known: print(cand)
