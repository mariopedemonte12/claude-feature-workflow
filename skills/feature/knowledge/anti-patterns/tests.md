# Seed catalog: tests

For unit, integration and end-to-end suites.

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| T-01 | Assertion-free or weak tests (only "does not throw", snapshot of everything) | Pass while behavior is wrong; mutation testing exposes them | Assert the specified outcome | Mutation testing; ast-grep on tests without assertions |
| T-02 | Testing implementation details (private calls, internal state) | Refactors break tests while behavior is intact | Test through the public behavior | Manual |
| T-03 | Over-mocking: mocks of the unit's own collaborators everywhere | Tests confirm the mocks, not the system | Mock only at external boundaries; use fakes | Manual |
| T-04 | Fixed sleeps in tests (`sleep`, `waitForTimeout`) | Slow and flaky | Wait for a condition; web-first assertions; fake clocks | ast-grep or ESLint (playwright/no-wait-for-timeout) |
| T-05 | Order-dependent tests sharing mutable data | Pass alone, fail together, or the reverse | Fresh data per test; isolated fixtures | Run in random order; manual |
| T-06 | E2E locators bound to CSS structure or generated classes | Break on any markup change | Role, label or test-id locators | ESLint playwright rules; ast-grep on locator strings |
| T-07 | Conditional logic inside tests | The test itself needs tests | One scenario per test; parameterized cases | ast-grep on if/loops in test bodies |
| T-08 | Skipped or quarantined tests without a tracking reason | Coverage silently shrinks | Fix, or `shortcut:` marker with the trigger to restore it | ast-grep on skip/only/xit |
| T-09 | Real external services in automated tests (payments, email, third-party APIs) | Flaky, slow, costly, side effects | Service virtualization or sandbox environments | Manual |
