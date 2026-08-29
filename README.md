# ACE-WSA Public Reproducibility Artifact - Post-Review Candidate

`v1.0.0` is immutable historical R2A-R2D evidence at commit
`00a5fb654ebd98b05de587a87f6a67cc0846643a` and Zenodo `10.5281/zenodo.22149310`.

This is a v1.1.0 candidate.

Post-review evidence:
- R2E-A: 26.5161% serialization, 20.9541% further admission, 41.9140% combined structural difference.
- R2E-B: 28/29 frozen predicates; `DUPLICATE` expected vs `AUTHORITY_OVERRIDDEN` actual; no repair.
- R2E-C: false-live vulnerability confirmed; equal-rank conflict still fails closed.

Code hardening adds `AUTHORITY_RELIABILITY_ADJUDICATION_REQUIRED` without silently promoting weaker authority.

The v1 mechanism is admission control + a priori working-set estimation, not demand paging.
WSA is conditional: Payload-WSA vs Provider/Wire-WSA.
