"""Duplicate one basename token's middle character."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts"))
import snapshot
tables=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
known=set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
for raw in sorted(known):
 n=raw.lower().replace('\\','/')
 if '/' not in n or '.' in n.rsplit('/',1)[-1]: continue
 d,b=n.rsplit('/',1); t=b.split('_')
 if len(t)<3 or any(len(x)<3 for x in t): continue
 for i,x in enumerate(t):
  k=len(x)//2; out=list(t); out[i]=x[:k]+x[k]+x[k:]
  c=d+'/'+'_'.join(out)
  if c not in known: print(c)
