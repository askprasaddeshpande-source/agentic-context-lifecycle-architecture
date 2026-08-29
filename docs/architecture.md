# Architecture - Post-Review Candidate

Mission -> Current State -> Retrieval -> Scope/Provenance -> Temporal Resolution ->
Authority-Reliability Adjudication -> Authority Resolution -> Deduplication ->
Planner -> Budget -> Compiler -> {Audit Plane, Model-Active Payload} -> Model -> Validation.

The v1 mechanism has no demand-fault path. Authority rank and reliability are distinct.
The reliability guard blocks for re-observation/adjudication and never silently reverses precedence.
Equal-rank contradictions remain `BLOCKED_CONFLICT`.
