from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class BaselineContext:
    tokens: int | None
    evidence_grade: str
    source: str | None = None

@dataclass(frozen=True)
class ShadowSafety:
    llm_calls: int = 0
    sap_calls: int = 0
    sap_writes: int = 0
    repository_writes: int = 0
    checkpoint_writes: int = 0
    capella_execution_path_changed: bool = False
    capella_prompt_changed: bool = False
    capella_model_changed: bool = False
    capella_tool_disclosure_changed: bool = False
    capella_governance_changed: bool = False
