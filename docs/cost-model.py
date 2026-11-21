CALLS_PER_FEATURE = 139 / 3
BASE_CTX = 30_000
GROWTH = (330_004 - BASE_CTX) / 139
MEASURED_ORCH_EQ = 3_814_093
SUBAGENT_EQ_PER_FEATURE = 4_417_189 / 3
BASELINE_EQ_PER_FEATURE = 625_908 / 3
USD_PER_EQ = 15.16 / (3_814_093 + 4_417_189)
WINDOW_CAP, AFTER_COMPACT, COMPACTION_EQ = 800_000, 150_000, 370_000


def cache_eq(calls, base, growth, cap=None):
    total, ctx, compactions = 0.0, base, 0
    for _ in range(int(calls)):
        total += 0.1 * ctx
        ctx += growth
        if cap and ctx > cap:
            ctx, compactions = AFTER_COMPACT, compactions + 1
    return total + compactions * COMPACTION_EQ, compactions


LINEAR_PER_CALL = (MEASURED_ORCH_EQ - cache_eq(139, BASE_CTX, GROWTH)[0]) / 139


def direct(n):
    calls = CALLS_PER_FEATURE * n
    cached, comp = cache_eq(calls, BASE_CTX, GROWTH, WINDOW_CAP)
    return cached + LINEAR_PER_CALL * calls, comp


def phased(n, principal_calls_per_feature=40, principal_growth=600, phases=5, runner_base=40_000):
    principal_calls = principal_calls_per_feature * n
    principal = cache_eq(principal_calls, BASE_CTX, principal_growth)[0] + principal_calls * (1.25 * principal_growth + 5 * 600)
    calls_per_phase = CALLS_PER_FEATURE / phases
    runner_phase = 1.25 * runner_base + cache_eq(calls_per_phase, runner_base, GROWTH)[0] + LINEAR_PER_CALL * calls_per_phase
    return principal + runner_phase * phases * n


def hierarchy_sessions(groups):
    subs = sum(direct(g)[0] for g in groups)
    calls = 40 * sum(groups)
    hub = cache_eq(calls, BASE_CTX, 600)[0] + calls * (1.25 * 600 + 5 * 600)
    return subs + hub


def row(name, orch, n):
    total = orch + SUBAGENT_EQ_PER_FEATURE * n
    base = BASELINE_EQ_PER_FEATURE * n
    print(f"{name:34} orch {orch/1e6:6.1f}M  total {total/1e6:6.1f}M  ${total*USD_PER_EQ:6.0f}  {total/base:5.1f}x baseline")


print(f"calibration: growth {GROWTH:.0f}/call, linear {LINEAR_PER_CALL:.0f} eq/call, ${USD_PER_EQ*1e6:.2f}/M eq")
for n in (3, 5, 10):
    print(f"--- {n} features, High (baseline {BASELINE_EQ_PER_FEATURE*n/1e6:.1f}M, ${BASELINE_EQ_PER_FEATURE*n*USD_PER_EQ:.0f})")
    d, comp = direct(n)
    row(f"direct ({comp} compactions)", d, n)
    row("phased", phased(n), n)
    row("phased, gates batched (-40% calls)", phased(n, principal_calls_per_feature=24), n)
    if n == 10:
        row("hierarchy, 3 sessions (3+3+4), direct", hierarchy_sessions([3, 3, 4]), n)
for n in range(2, 8):
    print(n, "direct", round(direct(n)[0]/1e6, 2), "phased", round(phased(n)/1e6, 2))
