from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, uuid

from .r2b_loader import load_r2b
from .builder import CapellaSnapshotBuilder
from .contracts import BaselineContext, ShadowSafety
from .estimator import estimate_tokens

def _canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",",":"), ensure_ascii=False, default=str)

def _sha256_bytes(b: bytes):
    return hashlib.sha256(b).hexdigest().upper()

def _baseline(snapshot: dict, candidate_tokens: int):
    b=snapshot.get("baseline_context",{})
    tokens=b.get("tokens")
    if tokens is not None:
        return BaselineContext(int(tokens),b.get("evidence_grade","MEASURED_RUNTIME"),b.get("source"))
    text=b.get("text")
    if text:
        return BaselineContext(estimate_tokens(text),"ESTIMATED_BASELINE_TEXT",b.get("source"))
    # Candidate pool is not identical to an actual prompt; explicitly grade it as estimate.
    return BaselineContext(candidate_tokens,"ESTIMATED_CANDIDATE_POOL","snapshot candidate set")

def run_shadow(snapshot: dict, *, r2b_root: str | None = None, evidence_root: str | Path | None = None):
    r2b=load_r2b(r2b_root)
    builder=CapellaSnapshotBuilder(r2b)
    mission=builder.mission(snapshot)
    candidates=builder.candidates(snapshot,mission)
    tools=builder.tools(snapshot)
    skills=builder.skills(snapshot)

    compiler=r2b["ContextCompiler"]()
    result=compiler.compile(mission,candidates,tools=tools,skills=skills,mode="SHADOW")
    status=result.status.value

    candidate_tokens=sum(c.estimated_tokens for c in candidates)
    baseline=_baseline(snapshot,candidate_tokens)
    safety=ShadowSafety()

    comparison={
        "schema_version":"r2c.1",
        "run_id":f"R2C-{uuid.uuid4()}",
        "mode":"READ_ONLY_SHADOW",
        "status":status,
        "mission_id":mission.mission_id,
        "baseline":{
            "tokens":baseline.tokens,
            "evidence_grade":baseline.evidence_grade,
            "source":baseline.source,
        },
        "candidate_pool":{
            "tokens":candidate_tokens,
            "records":len(candidates),
            "tools_available":len(tools),
            "skills_available":len(skills),
        },
        "compiled":None,
        "quality":None,
        "safety":asdict(safety),
        "blocking_conditions":result.blocking_conditions,
        "compiler":{
            "r2b_version":getattr(r2b["package"],"__version__","unknown"),
            "r2c_version":"0.1.0",
        },
    }

    if result.context:
        ctx=result.context
        totals=ctx.provenance_manifest["totals"]
        included_ids={x["candidate_id"] for x in ctx.provenance_manifest["included"]}
        mandatory=[c for c in candidates if c.mandatory or c.priority.value=="P0"]
        mandatory_preserved=sum(1 for c in mandatory if c.candidate_id in included_ids)
        superseded_included=sum(
            1 for c in candidates
            if c.temporal.state.value=="SUPERSEDED" and c.candidate_id in included_ids
        )
        compiled_tokens=totals["compiled_tokens"]
        baseline_tokens=baseline.tokens
        reduction=None
        amplification=None
        if baseline_tokens and baseline_tokens>0:
            reduction=round((1-compiled_tokens/baseline_tokens)*100,4)
            amplification=round(baseline_tokens/max(1,compiled_tokens),4)

        required_authorities={a.upper() for a in mission.validation.authorities}
        available_included=set()
        for c in candidates:
            if c.candidate_id in included_ids:
                available_included.add(c.authority_class.upper())
                st=str(c.provenance.get("source_type","")).upper()
                if st: available_included.add(st)
        auth_required=len(required_authorities)
        auth_present=len(required_authorities & available_included)
        auth_coverage=1.0 if auth_required==0 else auth_present/auth_required

        comparison["compiled"]={
            "tokens":compiled_tokens,
            "candidate_tokens":totals["compiled_candidate_tokens"],
            "capability_tokens":totals["capability_tokens"],
            "avoided_tokens":totals["avoided_tokens"],
            "context_hash":ctx.context_hash,
            "tools_selected":len(ctx.tools),
            "skills_selected":len(ctx.skills),
            "tool_disclosure_ratio":round(len(ctx.tools)/max(1,len(tools)),4) if tools else 0.0,
            "skill_disclosure_ratio":round(len(ctx.skills)/max(1,len(skills)),4) if skills else 0.0,
            "baseline_to_compiled_ratio":amplification,
            "context_reduction_pct_vs_baseline":reduction,
        }
        comparison["quality"]={
            "mandatory_facts_required":len(mandatory),
            "mandatory_facts_preserved":mandatory_preserved,
            "mandatory_fact_preservation_pct":round(100*mandatory_preserved/max(1,len(mandatory)),4),
            "authority_required_count":auth_required,
            "authority_present_count":auth_present,
            "authority_coverage":round(auth_coverage,4),
            "superseded_facts_injected":superseded_included,
            "provenance_coverage":ctx.provenance_manifest["coverage"]["included_provenance_count"]/
                                  max(1,ctx.provenance_manifest["coverage"]["included_count"]),
            "exclusion_reason_coverage":ctx.provenance_manifest["coverage"]["exclusion_reason_count"]/
                                        max(1,ctx.provenance_manifest["coverage"]["excluded_count"]),
        }

    artifacts={}
    if evidence_root is not None:
        root=Path(evidence_root)
        run_dir=root/comparison["run_id"]
        (run_dir/"INPUT").mkdir(parents=True,exist_ok=True)
        (run_dir/"RESULTS").mkdir(parents=True,exist_ok=True)

        snap_bytes=(json.dumps(snapshot,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
        (run_dir/"INPUT"/"snapshot.json").write_bytes(snap_bytes)
        (run_dir/"INPUT"/"snapshot.sha256").write_text(_sha256_bytes(snap_bytes)+"\n",encoding="utf-8")

        (run_dir/"RESULTS"/"shadow-comparison.json").write_text(json.dumps(comparison,indent=2)+"\n",encoding="utf-8")
        (run_dir/"RESULTS"/"telemetry.json").write_text(json.dumps(result.telemetry,indent=2)+"\n",encoding="utf-8")

        if result.context:
            (run_dir/"RESULTS"/"compiled-context.json").write_text(json.dumps(result.context.to_dict(),indent=2)+"\n",encoding="utf-8")
            (run_dir/"RESULTS"/"provenance-manifest.json").write_text(json.dumps(result.context.provenance_manifest,indent=2)+"\n",encoding="utf-8")

        q=comparison.get("quality") or {}
        c=comparison.get("compiled") or {}
        lines=[
            "ACE_WSA_R2C_CAPELLA_SHADOW="+("PASS" if status=="COMPILED" else status),
            f"RUN_ID={comparison['run_id']}",
            f"MISSION_ID={comparison['mission_id']}",
            f"BASELINE_TOKENS={comparison['baseline']['tokens']}",
            f"BASELINE_EVIDENCE_GRADE={comparison['baseline']['evidence_grade']}",
            f"CANDIDATE_POOL_TOKENS={comparison['candidate_pool']['tokens']}",
            f"COMPILED_TOKENS={c.get('tokens')}",
            f"CONTEXT_REDUCTION_PCT={c.get('context_reduction_pct_vs_baseline')}",
            f"BASELINE_TO_COMPILED_RATIO={c.get('baseline_to_compiled_ratio')}",
            f"MANDATORY_FACT_PRESERVATION_PCT={q.get('mandatory_fact_preservation_pct')}",
            f"AUTHORITY_COVERAGE={q.get('authority_coverage')}",
            f"SUPERSEDED_FACTS_INJECTED={q.get('superseded_facts_injected')}",
            "LLM_CALLS=0",
            "SAP_CALLS=0",
            "SAP_WRITES=0",
            "REPOSITORY_WRITES=0",
            "CAPELLA_EXECUTION_PATH_CHANGED=false",
        ]
        (run_dir/"SUMMARY.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
        artifacts={"run_dir":str(run_dir)}

    return comparison, result, artifacts
