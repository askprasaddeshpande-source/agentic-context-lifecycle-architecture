import unittest

from ace_wsa_r2b.compiler import ContextCompiler
from ace_wsa_r2b.fixtures import helios_mission, helios_candidates
from ace_wsa_r2b.models import (
    CandidateScores, CandidateScope, CompileStatus, ContextBudget, ContextCandidate,
    ExecutionPolicy, MissionEnvironment, MissionRequest, Priority, RiskProfile,
    TemporalInfo, TemporalState, ValidationPolicy,
)


def mission():
    return MissionRequest(
        mission_id="POST-REVIEW-RELIABILITY",
        intent="VERIFY_CURRENT_STATE",
        goal="Resolve current state without silent authority reversal.",
        environment=MissionEnvironment(project_id="P", system="S", client="001"),
        execution=ExecutionPolicy("PREVIEW", False, False),
        risk=RiskProfile("HIGH", "LOW", "HIGH"),
        validation=ValidationPolicy(True, ()),
        budget=ContextBudget(4000, 3000, 500),
    )


def candidate(cid, authority_class, value, validation):
    return ContextCandidate(
        candidate_id=cid,
        source_kind="CURRENT_STATE" if authority_class == "LIVE_ENTERPRISE_STATE" else "EVIDENCE",
        source_id=cid,
        content={"value": value},
        estimated_tokens=40,
        priority=Priority.P0 if authority_class == "LIVE_ENTERPRISE_STATE" else Priority.P2,
        scores=CandidateScores(.95, .95, 1.0, validation, .9),
        authority_class=authority_class,
        validation_state="VERIFIED" if validation >= .9 else "OBSERVED",
        temporal=TemporalInfo(TemporalState.CURRENT),
        scope=CandidateScope(project_id="P", system="S", client="001"),
        subject="runtime_status",
        value=value,
        provenance={"source_type": authority_class, "source_id": cid},
    )


class ReliabilityAdjudication(unittest.TestCase):
    def test_false_live_blocks_for_adjudication(self):
        r=ContextCompiler().compile(mission(),[
            candidate("LIVE-FALSE","LIVE_ENTERPRISE_STATE","AVAILABLE",.20),
            candidate("MEM-STRONG","VERIFIED_MEMORY","BLOCKED",.95)])
        self.assertEqual(r.status,CompileStatus.BLOCKED_CURRENT_STATE)
        self.assertEqual(r.blocking_conditions[0]["type"],
                         "AUTHORITY_RELIABILITY_ADJUDICATION_REQUIRED")

    def test_equal_rank_conflict_is_preserved(self):
        r=ContextCompiler().compile(mission(),[
            candidate("LIVE-A","LIVE_ENTERPRISE_STATE","AVAILABLE",.95),
            candidate("LIVE-B","LIVE_ENTERPRISE_STATE","BLOCKED",.95)])
        self.assertEqual(r.status,CompileStatus.BLOCKED_CONFLICT)

    def test_high_confidence_current_authority_still_wins(self):
        r=ContextCompiler().compile(mission(),[
            candidate("LIVE-STRONG","LIVE_ENTERPRISE_STATE","AVAILABLE",.95),
            candidate("MEM-STRONG","VERIFIED_MEMORY","BLOCKED",.99)])
        self.assertEqual(r.status,CompileStatus.COMPILED)
        included={x["candidate_id"] for x in r.context.provenance_manifest["included"]}
        self.assertIn("LIVE-STRONG",included)
        excluded={x["candidate_id"]:x["reason"] for x in r.context.provenance_manifest["excluded"]}
        self.assertEqual(excluded["MEM-STRONG"],"AUTHORITY_OVERRIDDEN")

    def test_existing_helios_fixture_unchanged(self):
        r=ContextCompiler().compile(helios_mission(),helios_candidates())
        self.assertEqual(r.status,CompileStatus.COMPILED)
        self.assertEqual(len(r.context.authoritative_state),10)


if __name__=="__main__":
    unittest.main()
