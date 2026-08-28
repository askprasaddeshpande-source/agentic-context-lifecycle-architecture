from .compiler import ContextCompiler
from .fixtures import helios_mission,helios_candidates
from .models import *

def mission(**kw):
    d=dict(mission_id="MIS-ACC",intent="TEST",goal="test",
        environment=MissionEnvironment(project_id="A",system="SYS",client="100"),
        execution=ExecutionPolicy("PREVIEW",False),risk=RiskProfile("HIGH"),
        validation=ValidationPolicy(True),budget=ContextBudget(1000,900,100),requested_capabilities=())
    d.update(kw);return MissionRequest(**d)

def c(cid,subject=None,value=None,authority="VERIFIED_MEMORY",temporal=TemporalState.CURRENT,
      priority=Priority.P2,tokens=20,mandatory=False,project="A",relevance=.9,provenance=True):
    return ContextCandidate(cid,"MEMORY",cid,{subject or "id":value if subject else cid},tokens,priority,
        CandidateScores(relevance,.9,1,.95,.9),authority,"VERIFIED",TemporalInfo(temporal),
        CandidateScope(project_id=project),subject,value,({"source_type":"TEST","source_id":cid} if provenance else {}),mandatory)

def run_acceptance():
    cc=ContextCompiler();checks={}
    h=cc.compile(helios_mission(),helios_candidates())
    checks["HELIOS_HISTORY_FILTER_TEST"]=h.status==CompileStatus.COMPILED and len(h.context.authoritative_state)==10 and len(h.context.tools)==0
    a=cc.compile(helios_mission(),helios_candidates(20));b=cc.compile(helios_mission(),helios_candidates(20))
    checks["DETERMINISTIC_REPLAY"]=a.context.context_hash==b.context.context_hash
    checks["CONTEXT_HASH_STABLE"]=checks["DETERMINISTIC_REPLAY"]
    r=cc.compile(mission(),[c("OLD","package","ZCLINE",temporal=TemporalState.SUPERSEDED),c("CUR","package","$TMP","CURRENT_POLICY",priority=Priority.P0,mandatory=True)])
    checks["TEMPORAL_SUPERSESSION"]=r.status==CompileStatus.COMPILED and any(x["value"]=="$TMP" for x in r.context.relevant_memory)
    r=cc.compile(mission(),[c("MEM","field","PLANE_TYPE","MODEL_GENERATED_MEMORY"),c("LIVE","field","LANGUAGE","SAP_METADATA")])
    checks["AUTHORITY_PRECEDENCE"]=r.status==CompileStatus.COMPILED and any(x["candidate_id"]=="LIVE" for x in r.context.relevant_memory)
    checks["UNRESOLVED_CONFLICT_FAIL_CLOSED"]=cc.compile(mission(),[c("A","target","A"),c("B","target","B")]).status==CompileStatus.BLOCKED_CONFLICT
    r=cc.compile(mission(),[c("M",priority=Priority.P0,mandatory=True,tokens=100),c("O",priority=Priority.P3,tokens=700)])
    checks["MANDATORY_CONTEXT_PRESERVATION"]=r.status==CompileStatus.COMPILED and any(x["candidate_id"]=="M" for x in r.context.relevant_memory)
    checks["HARD_BUDGET_ENFORCEMENT"]=cc.compile(mission(budget=ContextBudget(100,90,10)),[c("BIG",priority=Priority.P0,mandatory=True,tokens=95)]).status==CompileStatus.BLOCKED_BUDGET
    r=cc.compile(mission(),[c("D1","same","x","VERIFIED_MEMORY"),c("D2","same","x","MODEL_GENERATED_MEMORY")])
    checks["DUPLICATE_ELIMINATION"]=r.status==CompileStatus.COMPILED and sum(x["subject"]=="same" for x in r.context.relevant_memory)==1
    tm=mission(requested_capabilities=("READ_META",))
    tools=[ToolDescriptor("READ","READ_META","READ_ONLY",estimated_schema_tokens=20),ToolDescriptor("WRITE","WRITE_META","WRITE",estimated_schema_tokens=20),ToolDescriptor("OTHER","OTHER","READ_ONLY",estimated_schema_tokens=20)]
    r=cc.compile(tm,[],tools=tools);checks["TOOL_DISCLOSURE_FILTERING"]=r.status==CompileStatus.COMPILED and [x["tool_id"] for x in r.context.tools]==["READ"]
    sm=mission(requested_capabilities=("RAP_GENERATION",))
    r=cc.compile(sm,[],skills=[SkillDescriptor("RAP","1.0",("RAP_GENERATION",),20),SkillDescriptor("OTHER","1.0",("OTHER",),20)])
    checks["SKILL_DISCLOSURE_FILTERING"]=r.status==CompileStatus.COMPILED and [x["skill_id"] for x in r.context.skills]==["RAP"]
    r=cc.compile(mission(),[c("S","x","1",project="A"),c("X","y","2",project="B")])
    checks["CROSS_SCOPE_ISOLATION"]=r.status==CompileStatus.COMPILED and any(x["candidate_id"]=="X" and x["reason"]=="WRONG_SCOPE" for x in r.context.exclusions)
    checks["REQUIRED_AUTHORITY_FAIL_CLOSED"]=cc.compile(mission(validation=ValidationPolicy(True,("SAP_METADATA",))),[c("MEM")]).status==CompileStatus.BLOCKED_CURRENT_STATE
    checks["MANDATORY_SCOPE_FAIL_CLOSED"]=cc.compile(mission(),[c("MX",project="B",priority=Priority.P0,mandatory=True)]).status==CompileStatus.BLOCKED_SCOPE
    checks["UNKNOWN_MANDATORY_FAIL_CLOSED"]=cc.compile(mission(),[c("MU",temporal=TemporalState.UNKNOWN,priority=Priority.P0,mandatory=True)]).status==CompileStatus.BLOCKED_CURRENT_STATE
    r=cc.compile(helios_mission(),helios_candidates(50));cov=r.context.provenance_manifest["coverage"]
    checks["PROVENANCE_COVERAGE"]=cov["included_count"]==cov["included_provenance_count"]
    checks["EXCLUSION_REASON_COVERAGE"]=cov["excluded_count"]==cov["exclusion_reason_count"]
    checks["SCHEMA_CONTRACTS"]=bool(r.context.schema_version and r.context.mission_id and r.context.provenance_manifest)
    checks["SHADOW_MODE_ZERO_EXECUTION_WRITES"]=r.context.mode=="SHADOW" and not any(e["event_type"] in {"EXECUTION_STARTED","CHECKPOINT_CREATED"} for e in r.telemetry)
    return checks

def main():
    cks=run_acceptance();ok=all(cks.values());print("ACE_WSA_R2B_REFERENCE_IMPLEMENTATION="+("PASS" if ok else "FAIL"))
    order=["SCHEMA_CONTRACTS","DETERMINISTIC_REPLAY","TEMPORAL_SUPERSESSION","AUTHORITY_PRECEDENCE",
    "UNRESOLVED_CONFLICT_FAIL_CLOSED","MANDATORY_CONTEXT_PRESERVATION","HARD_BUDGET_ENFORCEMENT",
    "DUPLICATE_ELIMINATION","TOOL_DISCLOSURE_FILTERING","SKILL_DISCLOSURE_FILTERING","CROSS_SCOPE_ISOLATION",
    "REQUIRED_AUTHORITY_FAIL_CLOSED","MANDATORY_SCOPE_FAIL_CLOSED","UNKNOWN_MANDATORY_FAIL_CLOSED",
    "PROVENANCE_COVERAGE","EXCLUSION_REASON_COVERAGE","CONTEXT_HASH_STABLE","HELIOS_HISTORY_FILTER_TEST",
    "SHADOW_MODE_ZERO_EXECUTION_WRITES"]
    for k in order:
        val="100_PERCENT" if k in {"PROVENANCE_COVERAGE","EXCLUSION_REASON_COVERAGE"} and cks[k] else ("PASS" if cks[k] else "FAIL")
        print(f"{k}={val}")
    return 0 if ok else 1
