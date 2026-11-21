# References

The research behind the design of the review cycle (`skills/feature/protocols/review-cycle.md`). It is kept here, outside the skills, so that no citation is loaded into an agent's context.

## Why each piece of the review cycle exists

- **Clean context.** A model monitoring actions that appear as its own earlier output misses high-risk and low-correctness actions more often than when the same actions come from someone else [1]. Harmful self-preference persists where the evaluator is wrong as a generator [3]. The evidence is not unanimous: one study found no detectable self-preference when authors judged fixes to their own drafts [2]. A fresh agent avoids the risk at the cost of one more delegation.
- **Verification.** Maximal criticism produces false findings. Adversarial, stage-gated review with refutation and empirical checks removed most candidates before they were acted on [4]. Several cooperating agents caught more bugs than single agents [5].
- **Round limit.** Iterative feedback improves outputs [6] [7], but in repair loops the first three to four iterations account for most of the achievable gain and later ones add little [8].

Most of these sources are recent arXiv preprints, not peer-reviewed. Treat them as support for the design, not as proof.

## Sources

1. Khullar, D., Hopkins, J., Wang, R., & Roger, F. (2026). *Self-Attribution Bias: When AI Monitors Go Easy on Themselves*. arXiv preprint arXiv:2603.04582. https://arxiv.org/abs/2603.04582
2. Guey, W., & Bougault, P. (2026). *Self-Preference Is Weak or Absent in Verifiable Instruction-Following Revision: A Four-Model Test Under Genuine Authorship*. arXiv preprint arXiv:2606.20093. https://arxiv.org/abs/2606.20093
3. Chen, W.-L., Wei, Z., Zhu, X., Feng, S., & Meng, Y. (2025). *Do LLM Evaluators Prefer Themselves for a Reason?* arXiv preprint arXiv:2504.03846. https://arxiv.org/abs/2504.03846
4. Agarwal, A. (2026). *Refute-or-Promote: An Adversarial Stage-Gated Multi-Agent Review Methodology for High-Precision LLM-Assisted Defect Discovery*. arXiv preprint arXiv:2604.19049. https://arxiv.org/abs/2604.19049
5. Rajan, S. (2025). *Multi-Agent Code Verification via Information Theory*. arXiv preprint arXiv:2511.16708. https://arxiv.org/abs/2511.16708
6. Madaan, A., Tandon, N., Gupta, P., et al. (2023). *Self-Refine: Iterative Refinement with Self-Feedback*. arXiv preprint arXiv:2303.17651. https://arxiv.org/abs/2303.17651
7. Arimbur, J. J. (2026). *How Many Tries Does It Take? Iterative Self-Repair in LLM Code Generation Across Model Scales and Benchmarks*. arXiv preprint arXiv:2604.10508. https://arxiv.org/abs/2604.10508
8. Kiecker, T., Reichmann, E., Kang, H., An, G., & Grunske, L. (2026). *Is Three the Magic Number? An Empirical Evaluation of LLM-Based Repair Loops*. arXiv preprint arXiv:2607.05197. https://arxiv.org/abs/2607.05197
