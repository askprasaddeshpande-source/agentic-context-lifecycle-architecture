from __future__ import annotations
from pathlib import Path
import sys

def load_r2b(root: str | None = None):
    if root:
        src = Path(root).resolve() / "src"
        if not src.exists():
            raise RuntimeError(f"R2B source directory not found: {src}")
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
    try:
        import ace_wsa_r2b
        from ace_wsa_r2b.compiler import ContextCompiler
        from ace_wsa_r2b.models import (
            MissionRequest, MissionEnvironment, ExecutionPolicy, RiskProfile,
            ValidationPolicy, ContextBudget, ContextCandidate, CandidateScores,
            CandidateScope, TemporalInfo, TemporalState, Priority,
            ToolDescriptor, SkillDescriptor, CompileStatus
        )
    except Exception as e:
        raise RuntimeError(
            "ACE-WSA R2B is not importable. Install R2B with `python -m pip install -e .` "
            "from the R2B root, set ACE_WSA_R2B_ROOT, or pass --r2b-root."
        ) from e
    return {
        "package": ace_wsa_r2b,
        "ContextCompiler": ContextCompiler,
        "MissionRequest": MissionRequest,
        "MissionEnvironment": MissionEnvironment,
        "ExecutionPolicy": ExecutionPolicy,
        "RiskProfile": RiskProfile,
        "ValidationPolicy": ValidationPolicy,
        "ContextBudget": ContextBudget,
        "ContextCandidate": ContextCandidate,
        "CandidateScores": CandidateScores,
        "CandidateScope": CandidateScope,
        "TemporalInfo": TemporalInfo,
        "TemporalState": TemporalState,
        "Priority": Priority,
        "ToolDescriptor": ToolDescriptor,
        "SkillDescriptor": SkillDescriptor,
        "CompileStatus": CompileStatus,
    }
