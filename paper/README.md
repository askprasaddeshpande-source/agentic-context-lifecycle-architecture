From Persistent Memory to Mission Working Sets:
An Authority-Aware Context Lifecycle Architecture for Agentic AI
Prasad Deshpande
Independent Researcher – Agentic AI Systems and Enterprise Architecture
ORCID: 0009-0008-1344-6585
Email: er.prasad.deshpande@gmail.com
Research & Architecture: prasaddeshpande.com
Abstract
Long-horizon AI agents accumulate conversation history, tool schemas, observations, retrieved evidence, execution
traces, and durable memory. A common implementation pattern allows some or all of that accumulated state to
remain computationally active on subsequent model calls. This creates a systems-level paradox: experience that should
reduce rediscovery can instead enlarge the inference working set. We investigate whether persistent agent knowledge
can remain broad while model-active context is compiled narrowly for each mission. We first measure historical-context
amplification across three agent runtimes. In two controlled OpenAI Codex experiments, resuming a historical session
required approximately 6.70–6.73× the model input of a fresh sufficient-context execution while preserving identical
10/10 outcomes. In a single Google Gemini CLI replication pair, deliberately unrelated synthetic history produced a
45.57× input amplification while both arms scored 10/10. In one Anthropic Claude Code budget-feasibility test, a
large historical session consumed approximately 669.7K input/cache components and exhausted a configured budget
before completing, whereas a fresh session completed the same self-contained task at 10/10 using 22.3K input/cache
components; because the historical arm did not complete, we do not treat this as an outcome-equivalent ratio.
Motivated by these observations, we propose the Agentic Context Lifecycle Architecture (ACLA) and a deterministic
Context Compiler that separates persistent memory, authority resolution, active context, caching, and validation. The
design was developed through a staged R2A–R2D program: executable contract and invariants (R2A), standalone
deterministic compiler (R2B), read-only shadow evaluation against a real enterprise engineering agent (R2C), and
controlled model execution (R2D). In the enterprise shadow, the compiler reduced an estimated 16.4K-token live
analysis context to 9.4K tokens (42.66% estimated structural reduction), preserving 100% of mandatory facts and
authority coverage while injecting zero explicitly superseded facts; this R2C result is not provider-metered input. In
two replicated R2D A/B executions using the same model, reasoning effort, output contract, read-only constraints,
and zero tools, the compiled working-set treatment preserved a perfect 12/12 deterministic outcome in all arms while
reducing provider-reported model input by 28.42% and 24.99%, respectively. The treatment arm was not faster, and
cache behavior differed materially across replicates, reinforcing that model-input reduction, caching, latency, compute,
and monetary cost are distinct dimensions.
A post-review evidence layer then tested three boundaries raised during external scientific review. A three-arm
structural experiment separated serialization from admission: identical semantics shrank from 4,650 to 3,417 UTF-
8 bytes under compact serialization (26.5161%), and deterministic admission further reduced the same compact
representation to 2,701 bytes (20.9541% relative to the compact all-semantics arm; 41.9140% end-to-end structural
difference). These structural measurements do not decompose the historical provider-metered R2D effect. A held-out
cold-chain logistics suite with a contract-derived validator frozen before compiler execution passed 28 of 29 deterministic
predicates; the sole preserved mismatch concerned the reported exclusion stage for an equivalent record (DUPLICATE
expected versus AUTHORITY_OVERRIDDEN observed), and the suite was not repaired or rerun. Finally, falsification
showed that a wrong highest-ranked live observation can propagate through deterministic precedence. These results
narrow the mechanism framing, causal interpretation, and correctness boundary without rewriting the frozen R2A–R2D
evidence.
We therefore make a bounded claim: for the enterprise mission studied, authority-aware context compilation reduced
actual model input without reducing validated task quality. The contribution is not a new transformer architecture; it
is an agent-runtime systems architecture that treats model context as a scarce working set rather than a persistence
layer. We position the work relative to memory hierarchies, retrieval-augmented generation, prompt compression,
long-context evaluation, agent memory, context engineering, and contemporaneous 2026 work on context lifecycles
and working sets. We conclude with a measurement framework that directly measures Working-Set Amplification,
Historical Context Tax, and Fresh Context Reduction while reserving outcome-normalized economics for future
instrumentation, and with a falsifiable design principle: the future agent should remember far more than it processes.
Keywords: agentic AI; context engineering; memory systems; working set; long-horizon agents; retrieval; prompt
compression; context caching; enterprise agents; AI systems architecture

v1.2.0 Public Implementation Update
