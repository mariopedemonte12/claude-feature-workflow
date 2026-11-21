# Seed catalog: back ends and APIs

For HTTP or RPC services, workers and data-access code.

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| B-01 | N+1 queries: a query per item inside a loop | Latency grows with data; database overload | Batch, join or preload | Manual; query-count assertions in tests |
| B-02 | Unvalidated input crossing the trust boundary | Injection, corrupted data, crashes | Validate and parse at the edge into typed values | Semgrep or ast-grep taint-like rules; manual |
| B-03 | String-built SQL or shell commands | Injection | Parameterized queries; argument arrays | Semgrep, ast-grep, Bandit, gosec |
| B-04 | Check-then-write without a transaction or lock | Races under concurrent requests | Atomic operations, constraints, transactions | Manual |
| B-05 | Unbounded queries or in-memory lists | Memory and latency blow up with data | Pagination and limits | Manual |
| B-06 | Internal errors leaked to clients (stack traces, SQL messages) | Information disclosure | Map to stable error responses; log details server-side | Manual; E2E negative tests |
| B-07 | Secrets in code or config committed to the repo | Credential leaks | Environment or secret manager | gitleaks, secret scanners |
| B-08 | Missing timeouts and retries policy on outbound calls | One slow dependency stalls the service | Explicit timeouts; bounded retries with backoff | ast-grep on client calls without timeout |
| B-09 | Non-idempotent handlers for retried operations (payments, webhooks) | Duplicate effects | Idempotency keys | Manual |
| B-10 | Authorization checked only in the UI or by obscurity | Direct API calls bypass it | Server-side checks per resource | Manual; E2E negative tests |
