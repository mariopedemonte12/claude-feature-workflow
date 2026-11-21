# Review Cycle Protocol

Code review is done by **clean agents**: a fresh subagent that never saw how the code was written reviews it from scratch, as critically as it can. In the full cycle, a second clean agent tries to refute each finding, confirmed findings are fixed, and a new clean critic reviews again.

Why each piece exists (sources under §References):

- **Clean context.** A model monitoring actions that appear as its own earlier output misses high-risk and low-correctness actions more often than when the same actions come from someone else [1]. Harmful self-preference persists where the evaluator is wrong as a generator [3]. The evidence is not unanimous: one study found no detectable self-preference when authors judged fixes to their own drafts [2]. A fresh agent avoids the risk at the cost of one more delegation.
- **Verification.** Maximal criticism produces false findings. Adversarial, stage-gated review with refutation and empirical checks removed most candidates before they were acted on [4]. Several cooperating agents caught more bugs than single agents [5].
- **Round limit.** Iterative feedback improves outputs [6] [7], but in repair loops the first three to four iterations account for most of the achievable gain and later ones add little [8].

Most of these sources are recent arXiv preprints, not peer-reviewed. Treat them as support for the design, not as proof.

## Review levels

| Level | What runs | Typical feature |
| --- | --- | --- |
| **R0 · Gate only** | The Implementer's quality gate and project lint. No review agent. | Mechanical change: rename, configuration, copy, dependency bump, a change that follows an existing pattern line by line |
| **R1 · Single critic** | One clean critic, in parallel with the Tester. Its findings go to the defects gate. | Standard feature with new logic of moderate size |
| **R2 · Review cycle** | Clean critic → clean verifier → automatic fixes → new clean critic, up to 3 rounds. | Every Critical feature; Standard features that are large or complex |

**Critical features always use R2.** The orchestrator states it; it does not ask.

### Recommending the level

This is the one verification decision where the orchestrator **recommends**: the programmer asked for it as a standing instruction. The recommendation goes in the plan gate (SDD Direct step 6, ESDD step 7), labeled *Recommendation*, with the evidence behind it:

- **Size:** files and components the plan touches; estimated changed lines.
- **Complexity:** new branching logic, state machines, parsers, concurrency, money, security, data writes or migrations, public interfaces, changes across several features or layers.
- **Criticality.**

**Start from the default:** the intensity default (Lite R0 · Medium R1 · High R2; Critical always R2) (`protocols/intensity.md`). Recommend a different level only with evidence: lower to R0 only for a mechanical change with no new branching logic, none of the risk areas above and a small diff (on the order of 50 changed lines); raise to R2 for several risk areas or a large diff. The recommendation always states the default and why it deviates, if it does. A standing acceptance of recommendations covers only the default; a deviation is asked every time (`protocols/neutral-decisions.md` rule 13). The programmer validates or changes the level; record it in `decisions/` and in the plan's verification depth.

**Re-check after implementation.** Before review starts, compare the real diff (`git diff --shortstat <base>`, the files touched, the risk areas reached) with the estimate. If it crosses into another level, state the facts and recommend again; the programmer validates.

## Clean context

A critic's brief contains only: the feature worktree, the base commit, its role file and the output path. It does **not** receive, and must not open: the specification, the plan, decisions, handoffs, the implementation report, delegations, earlier review rounds, or anything else in the feature folder. It reads the code, `git diff <base>`, the project's own conventions (CLAUDE.md, lint configuration), the quality standard and the anti-pattern registry.

Each round launches a **new** critic. Never reuse a critic through SendMessage. Scope compliance against the spec is not the critic's job: the Tester validates the acceptance criteria and the orchestrator checks the implementation report against the plan.

## R2 · The cycle

```
round n:  Critic(n) ──► Verifier(n) ──► VALID behavior-preserving findings ──► Implementer fixes
              ▲                          everything else ──► defects gate        │
              └────────── tests + quality gate pass ◄────────────────────────────┘
```

1. **Critic** (`roles/reviewer.md`) writes `reports/review/round-<n>-critic.md`.
2. **Verifier** (`roles/verifier.md`), also clean, receives that report and tries to refute each finding against the code. Verdicts: VALID, INVALID, AMBIGUOUS. It classifies each VALID finding's fix as **behavior-preserving** (rename, extract, split by responsibility, remove duplication, remove code that this change itself left unused, simplify control flow, move to the right folder, without changing observable behavior or public interfaces; tests pass before and after) or **behavior-changing** (anything that changes outputs, errors, interfaces, the spec or the plan). It writes `reports/review/round-<n>-verification.md`.
3. **Fixes.** VALID behavior-preserving findings of severity Blocker, Major or Minor go to the Implementer without a gate. It fixes them, runs the affected tests and the quality gate, and records what it changed per finding ID. Behavior-changing findings, AMBIGUOUS findings and every Blocker that touches correctness or security go to the ⛔ defects gate. Nits are collected for the final report, not fixed in the loop.
4. **Next round** with a new critic on the **diff since the previous round** (the fixes), reporting only Blocker and Major findings. Round 1 is the only one that reviews the whole diff from the base.

**Stop when:**
- a round produces no new Blocker or Major finding; or
- the feature has had 3 critic rounds in total, counting every path (R1, R2 and the critics after defect fixes); or
- the loop oscillates: a finding asks to undo an earlier fix, or the same location is flagged again for the same problem after being fixed. Present the oscillation at the ⛔ defects gate.

After the loop, the Tester re-runs the regression suite and the E2E scenarios affected by the fixes.

## R1 · Single critic

The critic runs once, in parallel with the Tester, with the same clean context. It double-checks each finding itself before reporting. All findings go to the ⛔ defects gate. **At R1 nothing is fixed automatically**, not even behavior-preserving findings: the orchestrator checks the validated level before routing any fix.

## Automatic fixes are visible

At R2, every automatic fix is listed at the next gate: finding ID, files and hunks changed, and a revert option. The orchestrator never originates a fix itself: a problem it notices in the diff becomes a finding like any other.

## Round log and feedback

The orchestrator keeps `reports/review/rounds.md`, one row per round: round · critic model · findings raised (Blocker/Major/Minor/Nit) · VALID / INVALID / AMBIGUOUS · fixed automatically · sent to the gate.

Feedback beyond the feature:
- A VALID finding that is likely to recur, or that appeared in more than one round, becomes an anti-pattern candidate (`protocols/anti-pattern-registry.md`). The verifier marks them; the orchestrator writes them to `reports/anti-pattern-candidates.md`.
- A VALID finding that matches an `automated` registry entry means its rule missed a case: record it as a candidate to fix the rule.
- The share of INVALID findings across features shows how noisy the critic is. Report it in the final report.

## References

1. Khullar, D., Hopkins, J., Wang, R., & Roger, F. (2026). *Self-Attribution Bias: When AI Monitors Go Easy on Themselves*. arXiv preprint arXiv:2603.04582. https://arxiv.org/abs/2603.04582
2. Guey, W., & Bougault, P. (2026). *Self-Preference Is Weak or Absent in Verifiable Instruction-Following Revision: A Four-Model Test Under Genuine Authorship*. arXiv preprint arXiv:2606.20093. https://arxiv.org/abs/2606.20093
3. Chen, W.-L., Wei, Z., Zhu, X., Feng, S., & Meng, Y. (2025). *Do LLM Evaluators Prefer Themselves for a Reason?* arXiv preprint arXiv:2504.03846. https://arxiv.org/abs/2504.03846
4. Agarwal, A. (2026). *Refute-or-Promote: An Adversarial Stage-Gated Multi-Agent Review Methodology for High-Precision LLM-Assisted Defect Discovery*. arXiv preprint arXiv:2604.19049. https://arxiv.org/abs/2604.19049
5. Rajan, S. (2025). *Multi-Agent Code Verification via Information Theory*. arXiv preprint arXiv:2511.16708. https://arxiv.org/abs/2511.16708
6. Madaan, A., Tandon, N., Gupta, P., et al. (2023). *Self-Refine: Iterative Refinement with Self-Feedback*. arXiv preprint arXiv:2303.17651. https://arxiv.org/abs/2303.17651
7. Arimbur, J. J. (2026). *How Many Tries Does It Take? Iterative Self-Repair in LLM Code Generation Across Model Scales and Benchmarks*. arXiv preprint arXiv:2604.10508. https://arxiv.org/abs/2604.10508
8. Kiecker, T., Reichmann, E., Kang, H., An, G., & Grunske, L. (2026). *Is Three the Magic Number? An Empirical Evaluation of LLM-Based Repair Loops*. arXiv preprint arXiv:2607.05197. https://arxiv.org/abs/2607.05197
