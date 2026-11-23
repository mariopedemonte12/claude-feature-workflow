---
name: measurement
kind: guide
summary: Vetting a measured number (speedup, regression, latency, throughput, eval result) before reporting or acting on it
use-in: [plan, test, review, audit]
signals:
  - terms: ["fast", "faster", "slow", "slower", "speedup", "regression", "latency", "throughput", "benchmark", "performance", "p50", "p95", "p99", "memory", "eval", "metric"]
---
# Measurement

Every number this workflow reports or decides on is vetted here first: a probe's timing table, a specialist's measurement, a before and after in a validation report, an option's cost at a plan gate, an eval result. Answer each question with evidence from a run, not a guess about the code. Adapted from the `benchmark-checklist` and `explain-the-number` skills of pstack (github.com/cursor/plugins, MIT).

## Before you run

- **Write the claim first,** in the words you would report ("the export is 30% faster at p50 on the 60k-row dataset"), the result that would change a decision, and the noise floor. The questions below test that sentence.
- Read the measurement script. Note what it times, counts and ignores.
- Check the machine: load average (`uptime`) and core count (`nproc`). If it is busy, find out what is running. If you cannot stop it, interleave the sides so both see the same noise, and say so.

## The questions

1. **Why not double?** Name the limiter: the resource or code path that bounds the result, from a profile or counters taken during a run. A guess from reading the code is not a limiter. Profile in a run you do not report, because profilers slow the work down. Use CPU per process (`top`, `pidstat`), a runtime profiler (`py-spy`, `node --cpu-prof`, `perf`), I/O wait and syscall counts (`strace -c`), and map the hot spot to source. Watch the load generator too: if it saturates first, you measured the load generator. If a change did not move the number, the limiter explains why.
2. **Was it tuned?** Run every side the way production runs it: release builds, production flags and environment, batching and transactions, connection pools, warm or cold caches as production sees them, the same versions and data. If one side runs on defaults, you compared configurations, not implementations. A limiter that is a setting (a commit per row, a debug build, a missing index) means that side is untuned: tune it and measure again, or pick no winner from that run.
3. **Did it break limits?** Do the arithmetic: bytes per second against disk and network bandwidth, operations per second times cost per operation against the cores, and the time saved against the time the changed piece took. Removing a piece that takes 10% of the run makes the run at most about 11% faster. A result past a limit measured something other than the work: a cache, a no-op, a bug.
4. **Did it error?** Count failures and non-success responses, and check that outputs are correct, not only present. Rejections are fast; timeouts and retries are slow. If the script does not count errors, add the count.
5. **Does it reproduce?** Run each side at least 5 times, alternating (A, B, A, B…) so warmup, lazy initialization, caches and drift favor neither. Report the median and the range. A gap smaller than the run-to-run spread is no measurable difference. When the call is close, use a rank-sum test or the harness's own statistics.
6. **Does it matter?** Next to any micro result, measure the end-to-end path a user waits on, with realistic sizes and concurrency, and report the micro result as a share of the whole. A helper that takes 1% of a request makes the request at most 1% faster.
7. **Did the work happen?** Confirm the work ran inside the timed region: the request reached the server, the rows were written, the bytes were read, the result was used. Lazy code (generators nobody iterates, promises nobody awaits, results a JIT can discard) and timeouts produce numbers for work that never happened.

**A quick ballpark** the programmer asked for: one run is enough, but still check questions 4 and 7, and say it is one run. A choice between options is never a ballpark: all seven apply.

**An eval result** (a prompt or skill change, a model comparison): ask whether every run did the task, whether the gap holds across trials and models, and whether the scenario matters.

## Reporting

- Lead with the verdict: faster, slower, no measurable difference, or **inconclusive**.
- Give the number with its unit, the run count, the range and the limiter: "p50 41 ms → 33 ms, median of 7 runs per side, range 32 to 35 ms after, bound by JSON parsing on one core."
- The verdict is inconclusive when a difference is claimed but the limiter is unnamed, a side ran untuned, or questions 4 and 7 were not checked. Name the gap. Inconclusive is not a pass.
- At a gate, a number in an option's fields (`protocols/decisions.md`) carries its run count, range and limiter, or is marked *Unknown*.
- A pull request body carries one primary number; the runs, range and limiter evidence go in the feature's reports.
