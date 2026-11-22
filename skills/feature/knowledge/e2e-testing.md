---
name: e2e-testing
kind: guide
summary: End-to-end tests through the real entry point: harnesses, flows, evidence
use-in: [test-design, test]
signals:
  - terms: ["page", "screen", "endpoint", "CLI", "command", "API", "user"]
---
# End-to-End Testing Guide

End-to-end (E2E) tests exercise the feature **the way its user does, through the real entry point**: the browser, the HTTP API, the CLI, the app. Unit and integration tests show the parts work. E2E shows the assembled system delivers the acceptance criteria.

The Tester owns E2E testing. It is mandatory for every feature with a user-facing or externally observable surface. Its status uses the same three values as the black-box techniques: **Applied**, **Not applicable** (with the reason: e.g. an internal refactor with no observable change, already covered by existing E2E suites that were re-run) or **Blocked** (with the reason and the residual risk).

## 1. Choose the harness by surface

Use what the project already has. Installing a harness, or downloading browsers for it, adds a dev dependency, which is a programmer decision settled at the plan gate. If the plan did not settle it, return to the orchestrator before installing anything.

| Surface | Harness | How the test drives it |
| --- | --- | --- |
| Web UI | Playwright (Cypress or WebdriverIO if the project already uses them) | Real browser against the running app |
| HTTP / RPC API | Playwright `request`, supertest, httpx + pytest, REST Assured, Go `net/http` against a started server | Real requests to the running service |
| CLI | The language's process API (subprocess, execa, `os/exec`) in a temporary directory | Real binary, arguments, stdin, environment |
| Mobile app | Maestro, Detox, Appium | Emulator or simulator |
| Desktop app | Playwright for Electron, WebDriver for Tauri or native apps | Real app process |
| Background jobs, queues, events | The real worker plus a test producer and consumer | Publish the input, wait on the observable output |
| No interactive surface (games, simulations, devices, schedulers, control logic) | A **simulation harness**: headless run, deterministic seed, fake or controllable clock, simulated devices or environment, scripted scenarios | Drive inputs over simulated time; assert observable state and outputs |

## 2. The environment

- Start the system the way it runs: the build or dev server, real configuration, a real database (containers through Testcontainers or docker compose, or the project's test database). Playwright's `webServer` option starts and waits for the app.
- **Fake only what is outside the system**: third-party APIs, payment providers, email, clocks. Use service virtualization (MSW, WireMock, Prism from an OpenAPI file, Playwright `page.route`) and state in the report what was faked and how.
- Every test creates its own data, or gets it from an isolated fixture, and does not depend on another test's state.
- Record the exact commands to start the environment and to run the suite, so anyone can reproduce the results.

## 3. Writing E2E tests

- One scenario per acceptance criterion at least, through the user's path. Add the main negative paths: invalid input, unauthorized access, a failing dependency.
- **Locators the user would recognize:** role and accessible name (`getByRole('button', { name: 'Export' })`), label, text, or an explicit `data-testid`. Never CSS structure or generated class names.
- **No fixed sleeps.** Wait for a condition: Playwright's web-first assertions (`await expect(locator).toBeVisible()`) retry automatically. For simulations, advance the controllable clock.
- Assert what the user observes: visible text, a URL, a downloaded file, an HTTP status and body, an exit code and output, a persisted record read back through the system.
- Authentication: log in once per role and reuse the stored session (Playwright `storageState`) unless login is the feature under test.
- Accessibility: when the feature adds UI and `@axe-core/playwright` (or equivalent) is available, run an accessibility scan on the new screens.
- Test code follows `knowledge/code-quality.md`: no comments, short functions, declarative names. Group page interactions in small page objects or fixtures per feature (`e2e/<feature>/…`), following the project's existing E2E layout if there is one.

## 4. Running and evidence

- Run headless in the worktree. Keep the evidence the harness produces on failure (Playwright traces with `trace: 'on-first-retry'`, screenshots, videos, logs) under the feature folder's `reports/e2e/`. Committing binary evidence is decided at integration.
- A flaky test is re-run once and reported as flaky, with the trace. Never add sleeps or retries to make it pass.
- A failing E2E test is a defect report: steps, expected result (spec ID), actual result, evidence path. The test is kept.

## 5. Exploratory pass

If browser or device tools are available to you (a Playwright MCP server, a browser extension), you may also explore the feature by hand around the acceptance criteria: unexpected inputs, navigation back and forth, refresh mid-flow, small viewports. Every finding that matters becomes a reproducible test or a reported defect. Exploration alone is not evidence of a passing criterion.

## 6. Reporting

In `reports/validation-report.md`, the E2E section lists: harness and version, environment (what was real and what was faked), command, scenarios with their AC IDs and result, flaky tests, evidence paths and status (Applied / Not applicable / Blocked).
