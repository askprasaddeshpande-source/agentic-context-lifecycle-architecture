# ACE-WSA Public Reproducibility Artifact v1.0.0

Public reproducibility artifact for:

**From Persistent Memory to Mission Working Sets: An Authority-Aware Context Lifecycle Architecture for Agentic AI**

## Scope

This release preserves the deterministic/public-safe portions of the R2A-R2D
research program:

- R2A executable architecture contract and invariants
- R2B deterministic Context Compiler reference implementation
- R2C sanitized authority-conflict shadow fixture and cryptographic evidence identifiers
- R2D controlled A/B protocol, deterministic validator, aggregate provider telemetry and metric derivation
- reproducibility acceptance and public-safety evidence

## Bounded empirical result

Across two controlled replicate pairs of the tested enterprise-agent mission,
provider-reported model input fell by **28.4227%** and **24.9866%**,
respectively, while all four raw and compiled executions achieved the full
**12/12 deterministic outcome contract**.

The descriptive midpoint/median of these two observations is 26.7046%. This is
not a population-level effect estimate and is not a claim of equivalent monetary
cost, compute, or latency reduction.

## Safety / provenance

The package excludes private enterprise observations, credentials, private
repositories, workstation-specific paths and generated Python cache artifacts.
The private R2C source snapshot and exact historical provider execution
environment are not publicly replayable.
