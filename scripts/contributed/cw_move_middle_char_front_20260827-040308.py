"""Move each token's middle character to its front, one token at a time."""
import os,sys
_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(
    os.path.join(_root, "scripts", "snapshot.py")
):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot
tables=("fnv1a_xmaterials","fnv1a_ximages","fnv1a_xmodels","fnv1a_xanims")
known=set(snapshot.table_names(*tables)); known.update(snapshot.confirmed_names())
for raw in sorted(known):
 n=raw.lower().replace('\\','/')
 if '/' not in n or '.' in n.rsplit('/',1)[-1]: continue
 d,b=n.rsplit('/',1); t=b.split('_')
 if len(t)<3 or any(not x for x in t): continue
 for i,x in enumerate(t):
  if len(x)<3: continue
  k=len(x)//2; out=list(t); out[i]=x[k]+x[:k]+x[k+1:]
  c=d+'/'+'_'.join(out)
  if c not in known: print(c)
