"""Stable-partition basename tokens by even/odd character length."""
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
 out=[x for x in t if len(x)%2==0]+[x for x in t if len(x)%2]
 cand=d+'/'+ '_'.join(out)
 if out!=t and cand not in known: print(cand)
