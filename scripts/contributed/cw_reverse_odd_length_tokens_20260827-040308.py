"""Reverse characters only in odd-length basename tokens."""
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
 out=[x[::-1] if len(x)%2 else x for x in t]
 if out!=t:
  c=d+'/'+'_'.join(out)
  if c not in known: print(c)
