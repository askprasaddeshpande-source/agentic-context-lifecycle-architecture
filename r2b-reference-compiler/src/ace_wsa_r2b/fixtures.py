from .models import *
HELIOS_PACKET={
"experiment_id":"HX-20260828-AB1","project":"HELIOS-R17","release":"R17.4","authority":"ControlPlane",
"api_port":9472,"write_policy":"EXPLICIT_APPROVAL_ONLY","max_retries":2,
"validated_root_cause":"worker lease starvation",
"rejected_hypothesis":"Queue latency is caused by TLS handshake",
"next_action":"run read-only lease saturation probe"}

def helios_mission():
    return MissionRequest("MIS-HELIOS-R2B","CONTROLLED_CONTEXT_ECONOMICS","Return authoritative HELIOS-R17 facts.",
        MissionEnvironment(project_id="HELIOS-R17"),ExecutionPolicy("PREVIEW",False,False),
        RiskProfile("LOW","LOW","LOW"),ValidationPolicy(True,("CONTROL_PACKET",)),
        ContextBudget(12000,9000,1000),("NO_TOOLS","NO_EXTERNAL_STATE"),())

def helios_candidates(history_records=3500):
    out=[]
    for i,(k,v) in enumerate(HELIOS_PACKET.items(),1):
        out.append(ContextCandidate(f"HEL-{i:03d}","AUTHORITY","HELIOS-CONTROL-PACKET",{k:v},24,Priority.P0,
            CandidateScores(1,1,1,1,1),"LIVE_ENTERPRISE_AUTHORITY","AUTHORITATIVE",
            TemporalInfo(TemporalState.CURRENT),CandidateScope(project_id="HELIOS-R17"),k,v,
            {"source_type":"CONTROL_PACKET","source_id":"HX-20260828-AB1"},True))
    for i in range(1,history_records+1):
        out.append(ContextCandidate(f"NEB-{i:06d}","MEMORY",f"NEBULA-R42-{i:06d}",
            {"archive_record":i,"project":"NEBULA-R42","state":("ARCHIVED","CLOSED","SUPERSEDED","REJECTED","OBSOLETE")[i%5]},
            67,Priority.P5,CandidateScores(.01,.35,.45,.35,.01),"UNVERIFIED_TEXT","UNVERIFIED",
            TemporalInfo(TemporalState.HISTORICAL),CandidateScope(shareable=True),provenance=
            {"source_type":"SYNTHETIC_ARCHIVE","source_id":"NEBULA-R42"}))
    return out
