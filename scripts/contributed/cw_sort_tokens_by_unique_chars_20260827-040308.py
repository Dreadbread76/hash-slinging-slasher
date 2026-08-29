"""Stable-sort basename tokens by number of distinct characters."""
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
 out=[x for _,x in sorted(enumerate(t), key=lambda p:(len(set(p[1])),p[0]))]
 if out!=t:
  c=d+'/'+ '_'.join(out)
  if c not in known: print(c)
