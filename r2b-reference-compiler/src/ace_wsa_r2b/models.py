from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

class TemporalState(str, Enum):
    CURRENT="CURRENT"
    HISTORICAL="HISTORICAL"
    SUPERSEDED="SUPERSEDED"
    CONFLICTING="CONFLICTING"
    UNKNOWN="UNKNOWN"

class Priority(str, Enum):
    P0="P0"; P1="P1"; P2="P2"; P3="P3"; P4="P4"; P5="P5"

class CompileStatus(str, Enum):
    COMPILED="COMPILED"
    BLOCKED_AUTHORITY="BLOCKED_AUTHORITY"
    BLOCKED_CONFLICT="BLOCKED_CONFLICT"
    BLOCKED_BUDGET="BLOCKED_BUDGET"
    BLOCKED_SCOPE="BLOCKED_SCOPE"
    BLOCKED_AUTHORIZATION="BLOCKED_AUTHORIZATION"
    BLOCKED_CURRENT_STATE="BLOCKED_CURRENT_STATE"

AUTHORITY_PRECEDENCE = {
    "LIVE_ENTERPRISE_AUTHORITY":0,
    "LIVE_ENTERPRISE_STATE":0,
    "SAP_RUNTIME":0,
    "SAP_METADATA":0,
    "VERIFIED_RUNTIME_RESULT":1,
    "COMPILER_VALIDATED":1,
    "VALIDATED_ARTIFACT":2,
    "APPROVED_ARCHITECTURE_DECISION":3,
    "CURRENT_POLICY":3,
    "VERIFIED_MEMORY":4,
    "CURRENT_USER_ASSERTION":5,
    "HISTORICAL_TOOL_OBSERVATION":6,
    "MODEL_GENERATED_MEMORY":7,
    "UNVERIFIED_TEXT":8,
}

@dataclass(frozen=True)
class MissionEnvironment:
    project_id: Optional[str]=None
    system: Optional[str]=None
    client: Optional[str]=None
    repository: Optional[str]=None
    package: Optional[str]=None

@dataclass(frozen=True)
class ExecutionPolicy:
    mode: str="PREVIEW"
    write_allowed: bool=False
    network_allowed: bool=False

@dataclass(frozen=True)
class RiskProfile:
    level: str="LOW"
    complexity: str="LOW"
    uncertainty: str="LOW"

@dataclass(frozen=True)
class ValidationPolicy:
    required: bool=True
    authorities: tuple[str,...]=()

@dataclass(frozen=True)
class ContextBudget:
    hard_limit:int=32000
    soft_limit:int=28000
    reserve:int=4000
    @property
    def usable_limit(self): return max(0, self.hard_limit-self.reserve)

@dataclass(frozen=True)
class MissionRequest:
    mission_id:str
    intent:str
    goal:str
    environment:MissionEnvironment=field(default_factory=MissionEnvironment)
    execution:ExecutionPolicy=field(default_factory=ExecutionPolicy)
    risk:RiskProfile=field(default_factory=RiskProfile)
    validation:ValidationPolicy=field(default_factory=ValidationPolicy)
    budget:ContextBudget=field(default_factory=ContextBudget)
    constraints:tuple[str,...]=()
    requested_capabilities:tuple[str,...]=()
    requires_historical_reasoning:bool=False

@dataclass(frozen=True)
class CandidateScores:
    relevance:float=.5
    authority:float=.5
    temporal:float=1.0
    validation:float=.5
    utility:float=.5
    def value(self):
        vals=(self.relevance,self.authority,self.temporal,self.validation,self.utility)
        out=1.0
        for v in vals: out*=max(0.0,min(1.0,v))
        return out

@dataclass(frozen=True)
class CandidateScope:
    project_id:Optional[str]=None
    system:Optional[str]=None
    client:Optional[str]=None
    environment:Optional[str]=None
    shareable:bool=False

@dataclass(frozen=True)
class TemporalInfo:
    state:TemporalState=TemporalState.CURRENT
    observed_at:Optional[str]=None
    valid_from:Optional[str]=None
    valid_to:Optional[str]=None
    superseded_by:Optional[str]=None

@dataclass(frozen=True)
class ContextCandidate:
    candidate_id:str
    source_kind:str
    source_id:str
    content:Any
    estimated_tokens:int
    priority:Priority=Priority.P2
    scores:CandidateScores=field(default_factory=CandidateScores)
    authority_class:str="UNVERIFIED_TEXT"
    validation_state:str="UNVERIFIED"
    temporal:TemporalInfo=field(default_factory=TemporalInfo)
    scope:CandidateScope=field(default_factory=CandidateScope)
    subject:Optional[str]=None
    value:Any=None
    provenance:dict[str,Any]=field(default_factory=dict)
    mandatory:bool=False
    @property
    def authority_rank(self): return AUTHORITY_PRECEDENCE.get(self.authority_class,999)
    @property
    def value_density(self): return self.scores.value()/max(1,self.estimated_tokens)

@dataclass(frozen=True)
class ToolDescriptor:
    tool_id:str
    capability:str
    mode:str="READ_ONLY"
    risk:str="LOW"
    requires_authorization:bool=False
    estimated_schema_tokens:int=0
    scope_project_id:Optional[str]=None

@dataclass(frozen=True)
class SkillDescriptor:
    skill_id:str
    version:str
    capabilities:tuple[str,...]
    estimated_context_tokens:int=0
    risk:str="LOW"
    scope_project_id:Optional[str]=None

@dataclass
class Exclusion:
    source_id:str
    candidate_id:str
    tokens_avoided:int
    reason:str
    detail:Optional[str]=None

@dataclass
class Included:
    source_id:str
    candidate_id:str
    tokens:int
    reason:str
    authority:float
    source_kind:str

@dataclass
class CompiledContext:
    schema_version:str
    context_id:str
    mission_id:str
    compiler_version:str
    mode:str
    budget:dict[str,Any]
    mission:dict[str,Any]
    authoritative_state:list[dict[str,Any]]
    validated_decisions:list[dict[str,Any]]
    relevant_memory:list[dict[str,Any]]
    evidence:dict[str,list[Any]]
    skills:list[dict[str,Any]]
    tools:list[dict[str,Any]]
    unknowns:list[dict[str,Any]]
    conflicts:list[dict[str,Any]]
    exclusions:list[dict[str,Any]]
    provenance_manifest:dict[str,Any]
    context_hash:str=""
    def to_dict(self): return asdict(self)

@dataclass
class CompileResult:
    status:CompileStatus
    context:Optional[CompiledContext]
    blocking_conditions:list[dict[str,Any]]
    telemetry:list[dict[str,Any]]
