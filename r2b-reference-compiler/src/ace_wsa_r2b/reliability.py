from collections import defaultdict
from dataclasses import dataclass
import json

from .models import TemporalState


def _value(candidate):
    value = candidate.value if candidate.subject is not None else candidate.content
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class AuthorityReliabilityPolicy:
    low_confidence_threshold: float = 0.50
    corroborated_confidence_threshold: float = 0.90
    min_confidence_gap: float = 0.30


class AuthorityReliabilityGuard:
    """Block for adjudication when strongest authority is materially unreliable.

    Weaker authority never silently wins. Equal-rank contradictions remain with
    AuthorityResolver.
    """

    def __init__(self, policy=None):
        self.policy = policy or AuthorityReliabilityPolicy()

    def evaluate(self, candidates):
        grouped = defaultdict(list)
        for candidate in candidates:
            if candidate.subject:
                grouped[candidate.subject].append(candidate)

        blockers = []
        for subject in sorted(grouped):
            active = [c for c in grouped[subject]
                      if c.temporal.state != TemporalState.SUPERSEDED]
            if len(active) < 2:
                continue

            strongest_rank = min(c.authority_rank for c in active)
            strongest_group = [c for c in active if c.authority_rank == strongest_rank]

            # Let the existing resolver preserve equal-rank contradiction semantics.
            if len({_value(c) for c in strongest_group}) > 1:
                continue

            strongest = sorted(
                strongest_group,
                key=lambda c: (-c.scores.validation, -c.scores.relevance,
                               c.estimated_tokens, c.candidate_id),
            )[0]

            if strongest.scores.validation >= self.policy.low_confidence_threshold:
                continue

            weaker = [
                c for c in active
                if c.authority_rank > strongest_rank
                and _value(c) != _value(strongest)
                and c.scores.validation >= self.policy.corroborated_confidence_threshold
                and (c.scores.validation - strongest.scores.validation)
                    >= self.policy.min_confidence_gap
            ]
            if not weaker:
                continue

            corroborating = sorted(
                weaker,
                key=lambda c: (-c.scores.validation, c.authority_rank, c.candidate_id),
            )[0]

            blockers.append({
                "type": "AUTHORITY_RELIABILITY_ADJUDICATION_REQUIRED",
                "subject": subject,
                "strongest_candidate_id": strongest.candidate_id,
                "strongest_authority_class": strongest.authority_class,
                "strongest_validation": strongest.scores.validation,
                "contradicting_candidate_id": corroborating.candidate_id,
                "contradicting_authority_class": corroborating.authority_class,
                "contradicting_validation": corroborating.scores.validation,
                "validation_gap": corroborating.scores.validation - strongest.scores.validation,
                "action": "REOBSERVE_OR_ADJUDICATE",
            })
        return blockers
