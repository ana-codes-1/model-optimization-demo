---
name: eps-demo-testing-solid
description: Testing strategy, coverage gates, and SOLID design rules for EPS AI vibe demos. Use when writing tests, refactoring for testability, or wiring CI test gates.
---

# EPS Demo — Testing & SOLID

## SOLID-friendly design (required)

The code must be unit-testable **without touching the real cloud**:

- Use dependency injection for every external dependency (HTTP, storage, AI client, clock, randomness).
- Keep interfaces narrow (one verb per interface where possible).
- No static I/O. No "new SomeClient()" inside business logic.
- Pure functions for any transformation logic. Push side effects to the edges.

If a piece of code is hard to unit test, that is a design smell — fix the design.

## Coverage gates (enforced in CI)

- **Backend:** ≥ 70% line coverage. PR fails below threshold.
- **Frontend:** ≥ 60% with component tests on critical paths. PR fails below threshold.

## Test pyramid (guidance — not gated)

- **Bulk:** fast unit tests (milliseconds each). The vast majority of tests.
- **Thin layer:** integration tests against shared dev Azure resources.
- **Top:** 1–2 Playwright smoke tests for the critical demo path. No flaky e2e suites.

## Security and operability matrix

For identity-scoped agent demos, test:

- own secret/container/role allowed and every sibling boundary denied;
- DLS document filtering and FLS field removal;
- search allowed while file open is independently denied;
- raw tool output cannot enter public events;
- stream sequencing, deduplication, realtime fallback, and terminal completion;
- Model Router response-model precedence over router aliases;
- evidence count semantics, citations, and explicit denials;
- history partition isolation, strong ETags/conflicts, quotas, and retention;
- file type/size/hash/expiry and browser-bound download claims;
- null-safe health rendering, no-model readiness, cache coalescing, and exact
  expected-denial classification;
- portrait-mobile overflow and keyboard operation; and
- generated HTML/diagram/source-viewer rendering.

Before release, run a small targeted live suite through the public/custom-domain
boundary: critical journey, one allow, one denial, health, model attribution,
telemetry query, and file download when applicable. Deterministic CI remains the
bulk of testing.

Validation helpers and subagents must not reset, clean, or mutate the developer's
shared checkout. Use isolated worktrees or read-only review processes.

## FAKE_AI mode (mandatory)

- Every AI call must be routable through a fake.
- `FAKE_AI=1` env var swaps the real AI client for a deterministic fake that returns canned/recorded responses.
- CI **always** sets `FAKE_AI=1` so tests are deterministic and free.
- Fixtures live under `tests/fixtures/ai/`.

## Optional items

- **OpenAPI contract** in `docs/api/` with generated frontend types — recommended, not required.
- **Lighthouse CI + axe-core** as PR checks — recommended, not gated.
- Storybook for the shared component library only.

## Tooling defaults (pick the one matching the stack)

- Python: `pytest`, `pytest-cov`, `httpx` for HTTP test client.
- .NET: `xUnit`, `coverlet`, `WebApplicationFactory` for integration tests.
- TypeScript backend (Node): `vitest` or `jest`, `supertest`.
- React: `vitest` + `@testing-library/react`.
- E2E: Playwright.

## Anti-patterns to refuse

- "I'll mock it later" — write code with seams now.
- Tests that call real Azure OpenAI in CI.
- Test names that don't describe behavior ("test1", "should work").
- Coverage-padding tests with no assertions.
