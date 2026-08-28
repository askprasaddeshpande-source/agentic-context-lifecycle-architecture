# ACE-WSA Thesis

The architecture separates:

1. **Memory** — what should be remembered?
2. **Retrieval** — what might matter now?
3. **Context** — what must become computationally active now?
4. **Cache** — how cheaply can repeated active context be processed?

R2B owns the deterministic context-admission boundary.

> RAG proposes. Context Compiler disposes.

Optimization target:

```text
min(ContextCost)

subject to:
  MandatoryAuthorityCoverage == 100%
  ValidatedOutcomeQuality >= required threshold
```

North star:

> The future agent should remember far more than it processes.
