from __future__ import annotations

EXPECTED = {
    "experiment_id": "R2D-CAPELLA-AB-001",
    "project_checkpoint_blocker": "LIVE_UX_ACCEPTANCE_PENDING",
    "factory_runtime_status": "BLOCKED",
    "factory_runtime_reason_code": "SAP_CONNECTION_FAILED",
    "rap_readiness": "BRIDGE_UNAVAILABLE",
    "bridge_reachable": False,
    "sap_write_authority": "NONE",
    "checkpoint_next_action": "Execute one fresh Full-Stack UX request through existing Govern -> Approval",
    "safe_to_execute_checkpoint_next_action_now": False,
    "current_availability_authority": "CURRENT_RUNTIME",
}

REQUIRED_PROHIBITED = {
    "BACKEND_EXECUTION_REDESIGN",
    "PROVEN_TOOLCHAIN_PROFILE_REOPENING",
}

def score_answer(answer):
    errors=[]
    score=0
    max_score=len(EXPECTED)+len(REQUIRED_PROHIBITED)

    if not isinstance(answer,dict):
        return {"score":0,"max_score":max_score,"pass":False,"errors":["Answer is not a JSON object"]}

    for key,expected in EXPECTED.items():
        actual=answer.get(key,"__MISSING__")
        if actual == expected:
            score += 1
        else:
            errors.append(f"{key}: expected={expected!r} actual={actual!r}")

    prohibited=set(answer.get("prohibited_reinvestigation") or [])
    for value in sorted(REQUIRED_PROHIBITED):
        if value in prohibited:
            score += 1
        else:
            errors.append(f"prohibited_reinvestigation missing {value!r}")

    return {
        "score":score,
        "max_score":max_score,
        "pass":score==max_score,
        "errors":errors,
    }
