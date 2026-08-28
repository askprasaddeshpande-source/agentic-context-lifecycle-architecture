import json
from collections import defaultdict

def _key(c):
    x={"subject":c.subject,"value":c.value} if c.subject is not None else c.content
    return json.dumps(x,sort_keys=True,separators=(",",":"),default=str)

class Deduplicator:
    def dedupe(self,candidates):
        groups=defaultdict(list)
        for c in candidates:groups[_key(c)].append(c)
        kept=[];dups=[]
        for k in sorted(groups):
            g=groups[k]
            w=sorted(g,key=lambda c:(c.authority_rank,-c.scores.validation,-c.scores.relevance,c.estimated_tokens,c.candidate_id))[0]
            kept.append(w)
            dups.extend((c,w) for c in g if c.candidate_id!=w.candidate_id)
        return kept,dups
