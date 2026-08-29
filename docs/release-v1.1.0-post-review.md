# v1.1.0 Post-Review Revision

This revision responds to an external Major Revision review while preserving the historical
v1.0.0 evidence and release lineage.

## Scientific changes

- Clarifies that the v1 Context Compiler implements authority-aware admission control and
  a priori mission working-set estimation; it does not implement demand paging.
- Adds R2E-A structural deconfounding:
  - 26.5161% serialization reduction (4,650 -> 3,417 UTF-8 bytes)
  - 20.9541% further admission reduction (3,417 -> 2,701)
  - 41.9140% combined structural payload difference
  - not a retroactive decomposition of historical provider-metered R2D input.
- Adds R2E-B held-out frozen-validator evidence:
  - 4 cases
  - 29 frozen predicates
  - 28 pass / 1 preserved mismatch
  - expected exclusion label `DUPLICATE`
  - observed exclusion label `AUTHORITY_OVERRIDDEN`
  - no post-hoc repair or score-improving rerun.
- Adds R2E-C falsification:
  - a false strongest live observation propagated in frozen v1.0.0;
  - equal-rank contradictory claims still fail closed.

## Code hardening

A new `AuthorityReliabilityGuard` runs before authority resolution. When a low-confidence
strongest authority materially contradicts strongly validated weaker evidence, compilation
blocks with:

`AUTHORITY_RELIABILITY_ADJUDICATION_REQUIRED`

The weaker source does not silently win; the system requires re-observation or adjudication.

## WSA terminology

The revision distinguishes:

- **Payload-WSA**: application-payload ratio under a fixed mission, validator, and representation.
- **Provider/Wire-WSA**: provider-reported model-input ratio under a fixed provider/runtime
  comparison.

## Historical immutability

The following remain unchanged:

- v1.0.0 commit: `00a5fb654ebd98b05de587a87f6a67cc0846643a`
- v1.0.0 release asset SHA256:
  `E8F16EE16A933DD664ADF796F942ADE69D596CA1B8B1D9AF27E49306625B44EA`
- version DOI: `10.5281/zenodo.22149310`
- concept DOI: `10.5281/zenodo.22149309`
- historical R2A-R2D measurements.

## Claim boundary

This release does not claim universal context reduction, equivalent monetary-cost or compute
savings, latency improvement, independent human validation, or factual correctness from
authority rank alone.
