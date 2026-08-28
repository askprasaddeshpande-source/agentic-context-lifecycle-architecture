from collections import defaultdict
import json
from .models import TemporalState

def _val(c):
    return json.dumps(c.value if c.subject is not None else c.content,sort_keys=True,separators=(",",":"),default=str)

class Resolution:
    def __init__(self):
        self.winners=[];self.overridden=[];self.conflicts=[]

class AuthorityResolver:
    def resolve(self,candidates):
        r=Resolution(); grouped=defaultdict(list)
        for c in candidates:
            if c.subject: grouped[c.subject].append(c)
            else:r.winners.append(c)
        for subject in sorted(grouped):
            group=grouped[subject]
            active=[c for c in group if c.temporal.state!=TemporalState.SUPERSEDED]
            if not active:continue
            rank=min(c.authority_rank for c in active)
            top=[c for c in active if c.authority_rank==rank]
            if len({_val(c) for c in top})>1:
                r.conflicts.append({"subject":subject,"status":"UNRESOLVED_CONFLICT",
                    "claims":[{"candidate_id":c.candidate_id,"value":c.value,"authority_class":c.authority_class}
                              for c in sorted(top,key=lambda x:x.candidate_id)]})
                continue
            winner=sorted(top,key=lambda c:(-c.scores.validation,-c.scores.relevance,c.estimated_tokens,c.candidate_id))[0]
            r.winners.append(winner)
            for c in group:
                if c.candidate_id!=winner.candidate_id and c.temporal.state!=TemporalState.SUPERSEDED:
                    r.overridden.append((c,winner))
        return r
