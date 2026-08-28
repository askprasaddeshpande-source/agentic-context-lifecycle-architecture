from .models import *
def mission_from_dict(d):
    e=d.get("environment",{});x=d.get("execution",{});r=d.get("risk",{});v=d.get("validation",{});b=d.get("budgets",d.get("budget",{}))
    return MissionRequest(d["mission_id"],d["intent"],d["goal"],
        MissionEnvironment(e.get("project_id"),e.get("system"),e.get("client"),e.get("repository"),e.get("package")),
        ExecutionPolicy(x.get("mode","PREVIEW"),bool(x.get("write_allowed",False)),bool(x.get("network_allowed",False))),
        RiskProfile(r.get("level","LOW"),r.get("complexity","LOW"),r.get("uncertainty","LOW")),
        ValidationPolicy(bool(v.get("required",True)),tuple(v.get("authorities",[]))),
        ContextBudget(int(b.get("hard_limit",b.get("max_context_tokens",32000))),
                      int(b.get("soft_limit",min(28000,int(b.get("max_context_tokens",32000))))),
                      int(b.get("reserve",b.get("reserve_tokens",4000)))),
        tuple(d.get("constraints",[])),tuple(d.get("requested_capabilities",[])),bool(d.get("requires_historical_reasoning",False)))

def candidate_from_dict(d):
    s=d.get("scores",{});sc=d.get("scope",{});t=d.get("temporal",{})
    return ContextCandidate(d["candidate_id"],d.get("source_kind","MEMORY"),d.get("source_id",d["candidate_id"]),d.get("content"),
        int(d.get("estimated_tokens",1)),Priority(d.get("priority","P2")),
        CandidateScores(float(s.get("relevance",.5)),float(s.get("authority",.5)),float(s.get("temporal",1)),
                        float(s.get("validation",.5)),float(s.get("utility",.5))),
        d.get("authority_class","UNVERIFIED_TEXT"),d.get("validation_state","UNVERIFIED"),
        TemporalInfo(TemporalState(t.get("state","CURRENT")),t.get("observed_at"),t.get("valid_from"),t.get("valid_to"),t.get("superseded_by")),
        CandidateScope(sc.get("project_id"),sc.get("system"),sc.get("client"),sc.get("environment"),bool(sc.get("shareable",False))),
        d.get("subject"),d.get("value"),dict(d.get("provenance",{})),bool(d.get("mandatory",False)))
