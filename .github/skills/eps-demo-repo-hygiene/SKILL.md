---
name: eps-demo-repo-hygiene
description: Repository hygiene standards — CI/CD, secret scanning, pre-commit, required files (CONTRIBUTING, CODEOWNERS, LICENSE, SECURITY.md), uniform CLI. Use when setting up a new repo or auditing an existing one.
---

# EPS Demo — Repo Hygiene

## Required files at repo root

- `README.md` — short on-ramp; links to `/docs/README.md`
- `CONTRIBUTING.md` — how to develop, test, and contribute
- `CODEOWNERS` — owning architect(s)
- `LICENSE` — MIT
- `SECURITY.md` — how to report a vulnerability (point at the org-standard email)
- `.gitignore`, `.editorconfig`
- `.vscode/` (tasks.json, launch.json, extensions.json) — see `eps-demo-devx`
- `.devcontainer/devcontainer.json`
- `infra/` (Bicep) — see `eps-demo-architecture`
- `docs/` — see `eps-demo-docs`
- `evals/` — see `eps-demo-ai-models`

## GitHub Actions CI/CD (required)

Workflow stages (in order):
1. **Lint + format check**
2. **Build**
3. **Test** with coverage gates (BE ≥ 70%, FE ≥ 60%) — set `FAKE_AI=1`
4. **PR preview deploy** to a SWA/ACA preview slot
5. **Production deploy on merge to main**

## Secret hygiene

- **GitHub Secret Scanning** + push protection: on.
- **Dependabot**: on for npm/pip/nuget/actions/bicep.
- No `.env` files in the repo. `.env.example` is fine and required.
- A **pre-commit hook** (Husky for JS, `pre-commit` for Python, native git hooks otherwise) runs: lint, format, typecheck, and a local secret scan (`gitleaks` or equivalent).
- Treat copied terminal output, generated corpora, source snippets, deployment
  manifests, and documentation as secret-scan inputs. Never commit external API
  keys, encoded keys, tokens, connection strings, or full private endpoint URLs.

## Uniform repo CLI (required)

Every demo exposes the same top-level commands. The implementation can be npm scripts, Makefile, or Just — the verbs are fixed:

- `dev` — run the full stack locally
- `test` — run all tests with coverage
- `lint` — lint + format check
- `deploy` — deploy via Bicep/azd

VS Code tasks wrap these. CI calls these. Architects type these. One vocabulary.

## Telemetry

- App Insights with PII scrubbed.
- Baseline events: page view, AI call, model selection.
- Every event is documented in `docs/telemetry/events.md`.

## Release hygiene

- Generated docs/assets are deterministic and validated for stale directives,
  raw Mermaid, escaped syntax-highlighter markup, and broken internal links.
- The app colophon identifies the deployed commit. Rebuild/redeploy after the
  release commit so it is not one revision behind.
- Temporary cloud runners, identities, roles, packages, containers, local
  archives, and diagnostics are removed and verified before handoff.
- Use a private repo only through the ADR/compliance exception. Do not publish a
  fork or patch containing sensitive source merely to work around SSO.

## Anti-patterns to refuse

- A repo without `/docs`.
- A repo without `.vscode/tasks.json` and a "Run All" task.
- A repo without CI test gates.
- A README that is the only documentation.
- Secrets in app settings or `.env` files.
