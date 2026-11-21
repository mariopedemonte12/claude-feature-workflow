# Cost estimates: direct vs phased orchestration

These are **estimates from a model**, not measurements, except for the 3-feature calibration row. The model is in [`cost-model.py`](cost-model.py); run `python3 docs/cost-model.py` to reproduce the numbers.

## Calibration (measured)

One complete run: 3 large features on Django 6.1, High intensity, SDD Direct, Sonnet, direct mode, with a simulated programmer over 13 turns.

| | Measured |
| --- | --- |
| Orchestrator | 139 calls, peak context 330k tokens, 3.81M input-equivalent tokens |
| Subagents | 38 agents, 4.42M input-equivalent tokens (1.47M per feature) |
| Total | 8.23M eq, USD 15.16 (≈ USD 1.84 per M eq) |
| Baseline (one plain session, same request) | 0.63M eq, USD 1.12 |

Input-equivalent weights: input ×1, cache write ×1.25, cache read ×0.1, output ×5.

## Lean pipeline (measured)

The same 3 Django features ran with `/feature-lean`: one session per feature, in parallel, with the same simulated programmer.

| | Lean | High (direct) | Baseline |
| --- | --- | --- | --- |
| Cost | USD 5.30 | USD 15.16 | USD 1.12 |
| × baseline | 4.7 | 13.5 | 1 |
| Tokens eq | 2.57M (sessions 2.08M, 3 critics 0.48M) | 8.23M | 0.63M |
| Programmer turns | 4 per feature | 13 | 0 |
| Hidden tests | 42/43 | 42/43 | 41/43 |
| `__eq__` raising inside `{% switch %}` | raises | renders the default | raises |

**Lean v2** (adds the nearest-analog comparison and the testing techniques): USD 5.64 (5.0× baseline), 2.73M eq, 4 turns per feature, hidden tests 42/43.
- **Both misses were turned into questions:** both v1 misses (the `__eq__` case and the whitespace case) appeared at gate 1 as explicit questions, each with the analog's behavior as a fact: `{% if %}` catches the exception, and `CharField` strips whitespace.
- **The simulated programmer departed from the analog both times:** it let the exception propagate and rejected the whitespace. So the remaining hidden-test miss and the probe's result are programmer decisions, not oversights.

Lean failed "surrounding whitespace stripped" because the programmer chose to reject whitespace, a legitimate reading of "rejects anything else". It passed "trailing newline rejected", which High and the baseline failed. This is n=1, with the same caveats as the calibration run.

## Model

- **Direct.**
  - The orchestrator makes about 46 calls per feature.
  - Each call re-reads the context as a cached read, and the context grows by about 2.2k tokens per call.
  - On top of that, each call has a fixed cost (writes and output) of about 9.5k eq, fitted to the measured run.
  - Above 800k tokens the context compacts down to 150k, at a cost of about 0.37M eq per compaction.
  - The re-read term grows with the square of the number of features.
- **Phased.**
  - The orchestrator makes about 40 calls per feature (gates, questions, recording), and its context grows about 600 tokens per call.
  - The orchestration work itself moves to 5 phase runners per feature. Each runner starts at 40k tokens of context and makes the same calls with the same growth, but only within its phase.
  - **Gates batched:** the orchestrator presents the ready gates of several features in one message, which cuts its calls by about 40%.
- **Subagents and baseline** scale linearly per feature.

## Results, High intensity

| Features | Mode | Orchestration | Total | USD | × baseline |
| --- | --- | --- | --- | --- | --- |
| 3 | direct (measured) | 3.8M | 8.2M | 15 | 13 |
| 3 | phased | 4.0M | 8.4M | 15 | 13 |
| 5 | direct | 8.6M | 16.0M | 29 | 15 |
| 5 | phased | 7.1M | 14.5M | 27 | 14 |
| 10 | direct (1 compaction) | 22.4M | 37.1M | 68 | 18 |
| 10 | phased | 16.6M | 31.3M | 58 | 15 |
| 10 | phased, gates batched | 12.5M | 27.2M | 50 | 13 |
| 10 | hierarchy, 3 sessions (3+3+4), direct | 21.1M | 35.8M | 66 | 17 |

Baseline for 10 features: 2.1M eq, about USD 4.

- **Break-even:** phased costs more than direct up to 3 simultaneous features and less from 4 on (3: 3.8M vs 4.0M; 4: 6.0M vs 5.5M of orchestration).
- **Subagents stay fixed:** 14.7M for 10 features is not changed by the mode. It is set by the intensity: Lite and Medium run fewer agents.

## Assumptions not measured

- Phased-mode parameters: orchestrator calls per feature, its growth per call, phases per feature, the runner's starting context, and the 40% fewer calls from batching.
- That 10 features need 10/3 times the orchestration calls of the measured 3-feature run.
- Compaction behavior at large windows. The only measurement, with a 100k window, aborted the session.
- High intensity for every feature. Mixed intensities change the subagent term the most.

Treat each estimated figure as ±30–50% until a phased run is measured.
