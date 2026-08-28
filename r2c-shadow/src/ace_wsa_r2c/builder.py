from __future__ import annotations
from .estimator import estimate_tokens

SECTION_DEFAULTS = {
    "current_state": {
        "source_kind": "CURRENT_STATE",
        "priority": "P0",
        "authority_class": "LIVE_ENTERPRISE_STATE",
        "validation_state": "AUTHORITATIVE",
        "temporal_state": "CURRENT",
        "mandatory": True,
        "relevance": 1.0,
        "authority": 1.0,
        "validation": 1.0,
        "utility": 1.0,
    },
    "validated_decisions": {
        "source_kind": "DECISION",
        "priority": "P1",
        "authority_class": "APPROVED_ARCHITECTURE_DECISION",
        "validation_state": "VERIFIED",
        "temporal_state": "CURRENT",
        "mandatory": False,
        "relevance": 0.9,
        "authority": 0.9,
        "validation": 0.95,
        "utility": 0.9,
    },
    "historical_support": {
        "source_kind": "MEMORY",
        "priority": "P3",
        "authority_class": "HISTORICAL_TOOL_OBSERVATION",
        "validation_state": "OBSERVED",
        "temporal_state": "HISTORICAL",
        "mandatory": False,
        "relevance": 0.35,
        "authority": 0.55,
        "validation": 0.7,
        "utility": 0.35,
    },
}

class CapellaSnapshotBuilder:
    def __init__(self, r2b):
        self.r2b = r2b

    def mission(self, snap: dict):
        M=self.r2b
        m=snap["mission"]
        env=m.get("environment",{})
        exe=m.get("execution",{})
        risk=m.get("risk",{})
        val=m.get("validation",{})
        budget=m.get("budget",m.get("budgets",{}))
        return M["MissionRequest"](
            mission_id=m["mission_id"],
            intent=m["intent"],
            goal=m["goal"],
            environment=M["MissionEnvironment"](
                project_id=env.get("project_id"),
                system=env.get("system"),
                client=env.get("client"),
                repository=env.get("repository"),
                package=env.get("package"),
            ),
            execution=M["ExecutionPolicy"](
                mode=exe.get("mode","PREVIEW"),
                write_allowed=bool(exe.get("write_allowed",False)),
                network_allowed=bool(exe.get("network_allowed",False)),
            ),
            risk=M["RiskProfile"](
                level=risk.get("level","HIGH"),
                complexity=risk.get("complexity","MEDIUM"),
                uncertainty=risk.get("uncertainty","MEDIUM"),
            ),
            validation=M["ValidationPolicy"](
                required=bool(val.get("required",True)),
                authorities=tuple(val.get("authorities",[])),
            ),
            budget=M["ContextBudget"](
                hard_limit=int(budget.get("hard_limit",budget.get("max_context_tokens",32000))),
                soft_limit=int(budget.get("soft_limit",28000)),
                reserve=int(budget.get("reserve",budget.get("reserve_tokens",4000))),
            ),
            constraints=tuple(m.get("constraints",[])),
            requested_capabilities=tuple(m.get("requested_capabilities",[])),
            requires_historical_reasoning=bool(m.get("requires_historical_reasoning",False)),
        )

    def _candidate(self, section: str, item: dict, mission):
        M=self.r2b
        d=SECTION_DEFAULTS[section]
        temporal_state=item.get("temporal_state",d["temporal_state"])
        if item.get("superseded_by"):
            temporal_state="SUPERSEDED"
        content=item.get("content",{})
        estimated=int(item.get("estimated_tokens") or estimate_tokens(content))
        scope=item.get("scope",{})
        scores=item.get("scores",{})
        return M["ContextCandidate"](
            candidate_id=item["id"],
            source_kind=item.get("source_kind",d["source_kind"]),
            source_id=item.get("source_id",item["id"]),
            content=content,
            estimated_tokens=estimated,
            priority=M["Priority"](item.get("priority",d["priority"])),
            scores=M["CandidateScores"](
                relevance=float(scores.get("relevance",item.get("relevance",d["relevance"]))),
                authority=float(scores.get("authority",item.get("authority",d["authority"]))),
                temporal=float(scores.get("temporal",1.0)),
                validation=float(scores.get("validation",item.get("validation",d["validation"]))),
                utility=float(scores.get("utility",item.get("utility",d["utility"]))),
            ),
            authority_class=item.get("authority_class",d["authority_class"]),
            validation_state=item.get("validation_state",d["validation_state"]),
            temporal=M["TemporalInfo"](
                state=M["TemporalState"](temporal_state),
                observed_at=item.get("observed_at"),
                valid_from=item.get("valid_from"),
                valid_to=item.get("valid_to"),
                superseded_by=item.get("superseded_by"),
            ),
            scope=M["CandidateScope"](
                project_id=scope.get("project_id",mission.environment.project_id),
                system=scope.get("system",mission.environment.system),
                client=scope.get("client",mission.environment.client),
                environment=scope.get("environment"),
                shareable=bool(scope.get("shareable",False)),
            ),
            subject=item.get("subject"),
            value=item.get("value"),
            provenance=dict(item.get("provenance",{
                "source_type": item.get("authority_class",d["authority_class"]),
                "source_id": item.get("source_id",item["id"])
            })),
            mandatory=bool(item.get("mandatory",d["mandatory"])),
        )

    def candidates(self, snap: dict, mission):
        out=[]
        for section in ("current_state","validated_decisions","historical_support"):
            for item in snap.get(section,[]):
                out.append(self._candidate(section,item,mission))
        return out

    def tools(self, snap: dict):
        M=self.r2b
        return [
            M["ToolDescriptor"](
                tool_id=x["tool_id"],
                capability=x["capability"],
                mode=x.get("mode","READ_ONLY"),
                risk=x.get("risk","LOW"),
                requires_authorization=bool(x.get("requires_authorization",False)),
                estimated_schema_tokens=int(x.get("estimated_schema_tokens",0)),
                scope_project_id=x.get("scope_project_id"),
            )
            for x in snap.get("available_tools",[])
        ]

    def skills(self, snap: dict):
        M=self.r2b
        return [
            M["SkillDescriptor"](
                skill_id=x["skill_id"],
                version=x.get("version","1.0"),
                capabilities=tuple(x.get("capabilities",[])),
                estimated_context_tokens=int(x.get("estimated_context_tokens",0)),
                risk=x.get("risk","LOW"),
                scope_project_id=x.get("scope_project_id"),
            )
            for x in snap.get("available_skills",[])
        ]
