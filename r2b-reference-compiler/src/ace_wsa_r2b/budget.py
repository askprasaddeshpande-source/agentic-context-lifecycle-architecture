from .models import Priority
RANK={Priority.P0:0,Priority.P1:1,Priority.P2:2,Priority.P3:3,Priority.P4:4,Priority.P5:5}

class BudgetController:
    def admit(self,candidates,budget):
        mandatory=[c for c in candidates if c.mandatory or c.priority==Priority.P0]
        optional=[c for c in candidates if c not in mandatory and c.priority!=Priority.P5]
        p5=[c for c in candidates if c.priority==Priority.P5]
        mandatory=sorted(mandatory,key=lambda c:c.candidate_id)
        mt=sum(c.estimated_tokens for c in mandatory)
        if mt>budget.usable_limit:
            return {"status":"BLOCKED_BUDGET","included":[],"excluded":optional+p5,"mandatory_tokens":mt,"used_tokens":0}
        inc=list(mandatory);used=mt;exc=list(p5)
        ordered=sorted(optional,key=lambda c:(RANK[c.priority],-c.value_density,c.authority_rank,-c.scores.relevance,c.estimated_tokens,c.candidate_id))
        for c in ordered:
            if used+c.estimated_tokens<=budget.usable_limit:
                inc.append(c);used+=c.estimated_tokens
            else:exc.append(c)
        return {"status":"COMPILED","included":inc,"excluded":exc,"mandatory_tokens":mt,"used_tokens":used}
