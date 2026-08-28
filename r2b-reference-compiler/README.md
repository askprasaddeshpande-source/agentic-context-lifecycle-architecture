# ACE-WSA R2B — Standalone Context Compiler Reference Implementation

## Thesis

**Persist broadly → resolve authority → retrieve selectively → compile minimally → validate rigorously.**

R2B is a deterministic reference implementation of the R2A Context Compiler contract.

Core invariants:

- `MEMORY != CONTEXT`
- `SESSION_HISTORY != REQUIRED_WORKING_SET`
- `RETRIEVAL != AUTHORITY`
- `CURRENT_AUTHORITY > HISTORICAL_MEMORY`
- `SUPERSEDED_FACTS_EXCLUDED_BY_DEFAULT`
- `CACHING_EFFICIENCY != CONTEXT_EFFICIENCY`
- `EVICT_FROM_CONTEXT != DELETE_EVIDENCE`
- `VALIDATED_OUTCOME` is the value boundary.

## Implemented

- Mission and candidate contracts
- Temporal/supersession resolution
- Hard authority precedence
- Conflict detection with fail-closed behavior
- Required-authority fail-closed behavior
- Mandatory cross-scope fail-closed behavior
- Mandatory provenance enforcement
- Deterministic de-duplication
- Candidate value-density scoring
- Context budget enforcement
- Dynamic tool disclosure
- Dynamic skill disclosure
- Provenance/exclusion manifest
- Stable context hashing
- Context telemetry
- HELIOS synthetic-history regression fixture
- Standalone CLI
- Executable acceptance suite

## Deliberately not implemented in R2B

- No LLM planner
- No embeddings/vector DB dependency
- No autonomous memory mutation
- No transcript deletion
- No SAP writes
- No repository writes
- No deployment
- No Capella execution changes

## Quick start

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
ace-r2b-acceptance
ace-context helios
```

## Acceptance gate

A valid reference build must emit:

```text
ACE_WSA_R2B_REFERENCE_IMPLEMENTATION=PASS
SCHEMA_CONTRACTS=PASS
DETERMINISTIC_REPLAY=PASS
TEMPORAL_SUPERSESSION=PASS
AUTHORITY_PRECEDENCE=PASS
UNRESOLVED_CONFLICT_FAIL_CLOSED=PASS
MANDATORY_CONTEXT_PRESERVATION=PASS
HARD_BUDGET_ENFORCEMENT=PASS
DUPLICATE_ELIMINATION=PASS
TOOL_DISCLOSURE_FILTERING=PASS
SKILL_DISCLOSURE_FILTERING=PASS
CROSS_SCOPE_ISOLATION=PASS
REQUIRED_AUTHORITY_FAIL_CLOSED=PASS
MANDATORY_SCOPE_FAIL_CLOSED=PASS
UNKNOWN_MANDATORY_FAIL_CLOSED=PASS
PROVENANCE_COVERAGE=100_PERCENT
EXCLUSION_REASON_COVERAGE=100_PERCENT
CONTEXT_HASH_STABLE=PASS
HELIOS_HISTORY_FILTER_TEST=PASS
SHADOW_MODE_ZERO_EXECUTION_WRITES=PASS
```

## R2C boundary

R2B remains standalone. The next step is a read-only Capella shadow adapter:

```text
Existing Capella execution ──────────────► unchanged

Same mission
   ↓
R2B Context Compiler
   ↓
candidate optimized context
   ↓
compare-only telemetry
```
