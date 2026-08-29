"""Reverse the relative order of tokens containing digits, preserving others."""
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
 idx=[i for i,x in enumerate(t) if any(c.isdigit() for c in x)]
 if len(idx)<2: continue
 out=list(t)
 for i,v in zip(idx,reversed([t[j] for j in idx])): out[i]=v
 if out!=t:
  c=d+'/'+'_'.join(out)
  if c not in known: print(c)
