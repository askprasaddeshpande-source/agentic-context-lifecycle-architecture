from dataclasses import asdict
from uuid import uuid4
from .models import *
from .scope import ScopePolicy
from .temporal import TemporalResolver
from .authority import AuthorityResolver
from .dedupe import Deduplicator
from .budget import BudgetController
from .capabilities import CapabilitySelector
from .canonical import stable_hash
from .telemetry import Telemetry

class ContextCompiler:
    VERSION="r2b.1"
    def __init__(self):
        self.scope=ScopePolicy();self.temporal=TemporalResolver();self.authority=AuthorityResolver()
        self.dedupe=Deduplicator();self.budget=BudgetController();self.capabilities=CapabilitySelector()

    def compile(self,mission,candidates,tools=(),skills=(),*,mode="SHADOW",mission_time=None):
        tel=Telemetry(mission.mission_id);tel.emit("MISSION_RECEIVED",{"intent":mission.intent,"mode":mode})
        candidates=list(candidates);ex=[]

        if mission.execution.mode.upper() in {"WRITE","EXECUTE","DEPLOY"} and not mission.execution.write_allowed:
            return CompileResult(CompileStatus.BLOCKED_AUTHORIZATION,None,[{"type":"WRITE_NOT_AUTHORIZED"}],tel.events)

        required={a.upper() for a in mission.validation.authorities}
        if mission.validation.required and required:
            available=set()
            for c in candidates:
                available.add(c.authority_class.upper())
                st=str(c.provenance.get("source_type","")).upper()
                if st:available.add(st)
            missing=sorted(required-available)
            if missing:
                return CompileResult(CompileStatus.BLOCKED_CURRENT_STATE,None,
                    [{"type":"REQUIRED_AUTHORITY_MISSING","authorities":missing}],tel.events)

        scoped=[];mandatory_scope=[];mandatory_prov=[]
        for c in candidates:
            ok,reason=self.scope.allowed(c,mission)
            if not ok:
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,reason or "WRONG_SCOPE"))
                if c.mandatory or c.priority==Priority.P0:mandatory_scope.append(c.candidate_id)
                continue
            if not c.provenance:
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,"UNVERIFIED","MISSING_PROVENANCE"))
                if c.mandatory or c.priority==Priority.P0:mandatory_prov.append(c.candidate_id)
                continue
            scoped.append(c)

        if mandatory_scope:
            return CompileResult(CompileStatus.BLOCKED_SCOPE,None,
                [{"type":"MANDATORY_SCOPE_VIOLATION","candidate_ids":sorted(mandatory_scope)}],tel.events)
        if mandatory_prov:
            return CompileResult(CompileStatus.BLOCKED_AUTHORITY,None,
                [{"type":"MANDATORY_PROVENANCE_MISSING","candidate_ids":sorted(mandatory_prov)}],tel.events)

        eligible=[];unknown=[]
        for c in scoped:
            c=self.temporal.resolve(c,mission_time)
            if c.temporal.state==TemporalState.SUPERSEDED:
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,"SUPERSEDED",c.temporal.superseded_by));continue
            if c.temporal.state==TemporalState.HISTORICAL and not mission.requires_historical_reasoning:
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,"HISTORICAL_NOT_REQUIRED"));continue
            if c.temporal.state==TemporalState.UNKNOWN and (c.mandatory or c.priority==Priority.P0) and mission.risk.level.upper() in {"HIGH","CRITICAL"}:
                unknown.append(c.candidate_id);continue
            eligible.append(c)
        if unknown:
            return CompileResult(CompileStatus.BLOCKED_CURRENT_STATE,None,
                [{"type":"UNKNOWN_MANDATORY_TEMPORAL_STATE","candidate_ids":sorted(unknown)}],tel.events)

        ar=self.authority.resolve(eligible)
        if ar.conflicts:
            return CompileResult(CompileStatus.BLOCKED_CONFLICT,None,ar.conflicts,tel.events)
        for loser,winner in ar.overridden:
            ex.append(Exclusion(loser.source_id,loser.candidate_id,loser.estimated_tokens,"AUTHORITY_OVERRIDDEN",winner.candidate_id))

        deduped,dups=self.dedupe.dedupe(ar.winners)
        for d,w in dups:ex.append(Exclusion(d.source_id,d.candidate_id,d.estimated_tokens,"DUPLICATE",w.candidate_id))

        planned=[]
        for c in deduped:
            if c.priority==Priority.P5 or (not c.mandatory and c.scores.relevance<.15):
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,"LOW_RELEVANCE"));continue
            planned.append(c)

        sel_tools,exc_tools=self.capabilities.select_tools(mission,list(tools))
        sel_skills,exc_skills=self.capabilities.select_skills(mission,list(skills))
        for t,r in exc_tools:ex.append(Exclusion(t.tool_id,t.tool_id,t.estimated_schema_tokens,r))
        for s,r in exc_skills:ex.append(Exclusion(s.skill_id,s.skill_id,s.estimated_context_tokens,r))
        cap_tokens=sum(t.estimated_schema_tokens for t in sel_tools)+sum(s.estimated_context_tokens for s in sel_skills)
        usable=mission.budget.usable_limit-cap_tokens
        if usable<0:return CompileResult(CompileStatus.BLOCKED_BUDGET,None,[{"type":"CAPABILITY_BUDGET_OVERFLOW"}],tel.events)

        b=ContextBudget(hard_limit=usable,soft_limit=min(mission.budget.soft_limit,usable),reserve=0)
        admitted=self.budget.admit(planned,b)
        if admitted["status"]!="COMPILED":
            return CompileResult(CompileStatus.BLOCKED_BUDGET,None,[{"type":"MANDATORY_CONTEXT_EXCEEDS_BUDGET",
                "mandatory_tokens":admitted["mandatory_tokens"],"usable_limit":usable}],tel.events)
        inc=admitted["included"]
        for c in admitted["excluded"]:
            if not any(e.candidate_id==c.candidate_id for e in ex):
                ex.append(Exclusion(c.source_id,c.candidate_id,c.estimated_tokens,"BUDGET"))

        auth=[];dec=[];mem=[];evidence=[];manifest_inc=[]
        for c in inc:
            item={"candidate_id":c.candidate_id,"source_id":c.source_id,"content":c.content,"subject":c.subject,
                  "value":c.value,"authority_class":c.authority_class,"validation_state":c.validation_state,
                  "estimated_tokens":c.estimated_tokens,"provenance":c.provenance}
            kind=c.source_kind.upper()
            if kind in {"CURRENT_STATE","AUTHORITY"}:auth.append(item)
            elif kind=="DECISION":dec.append(item)
            elif kind=="EVIDENCE":evidence.append(item)
            else:mem.append(item)
            reason="MANDATORY_AUTHORITY" if (c.mandatory or c.priority==Priority.P0) and kind in {"CURRENT_STATE","AUTHORITY"} \
                else "MANDATORY_MISSION" if c.mandatory or c.priority==Priority.P0 else "HIGH_RELEVANCE"
            manifest_inc.append(Included(c.source_id,c.candidate_id,c.estimated_tokens,reason,c.scores.authority,c.source_kind))

        candidate_tokens=sum(c.estimated_tokens for c in candidates)
        compiled_candidate_tokens=sum(c.estimated_tokens for c in inc)
        compiled_tokens=compiled_candidate_tokens+cap_tokens
        ex_out=[asdict(x) for x in sorted(ex,key=lambda x:(x.reason,x.candidate_id))]
        inc_out=[asdict(x) for x in sorted(manifest_inc,key=lambda x:x.candidate_id)]
        manifest={"included":inc_out,"excluded":ex_out,
            "totals":{"available_candidate_tokens":candidate_tokens,"compiled_candidate_tokens":compiled_candidate_tokens,
                      "capability_tokens":cap_tokens,"compiled_tokens":compiled_tokens,
                      "avoided_tokens":sum(x.tokens_avoided for x in ex)},
            "coverage":{"included_count":len(inc),"included_provenance_count":sum(1 for c in inc if c.provenance),
                        "excluded_count":len(ex_out),"exclusion_reason_count":sum(1 for x in ex_out if x["reason"])}}

        ctx=CompiledContext("r2b.1",f"CC-{uuid4()}",mission.mission_id,self.VERSION,mode,
            {"hard_limit":mission.budget.hard_limit,"soft_limit":mission.budget.soft_limit,"reserve":mission.budget.reserve,
             "usable_limit":mission.budget.usable_limit,"compiled_tokens_estimated":compiled_tokens},
            {"intent":mission.intent,"goal":mission.goal,"execution_mode":mission.execution.mode,
             "write_allowed":mission.execution.write_allowed,"risk":mission.risk.level,"constraints":list(mission.constraints)},
            auth,dec,mem,{"inline":evidence,"references":[]},[asdict(s) for s in sel_skills],[asdict(t) for t in sel_tools],
            [],[],ex_out,manifest)
        h=ctx.to_dict();h.pop("context_id",None);h.pop("context_hash",None);ctx.context_hash=stable_hash(h)
        tel.emit("CONTEXT_COMPILED",{"context_hash":ctx.context_hash,"compiled_tokens":compiled_tokens,
            "avoided_tokens":manifest["totals"]["avoided_tokens"],"tool_count":len(sel_tools),"skill_count":len(sel_skills),"mode":mode})
        return CompileResult(CompileStatus.COMPILED,ctx,[],tel.events)
