# Agent Guidance for this Repository

This repository is a **template** for EPS AI partner-facing "vibe-coded"
demos. Agents working here (GitHub Copilot in VS Code, Copilot CLI, Copilot
cloud agent, Codex, Cursor) must follow the standards below — both when
bootstrapping a brand-new demo from this template and when working in a repo
that was already generated from it.

## Authoritative source

The full standards live in `.github/skills/`. Each subfolder is a
self-contained skill with a `SKILL.md`. **Load the relevant skill before
acting**, especially `eps-demo-standards` first.

| Concern | Skill |
|---|---|
| Master / routing | `.github/skills/eps-demo-standards/SKILL.md` |
| Azure & Bicep | `.github/skills/eps-demo-architecture/SKILL.md` |
| UX & a11y | `.github/skills/eps-demo-ux/SKILL.md` |
| Identity & auth | `.github/skills/eps-demo-identity/SKILL.md` |
| Testing & SOLID | `.github/skills/eps-demo-testing-solid/SKILL.md` |
| Documentation | `.github/skills/eps-demo-docs/SKILL.md` |
| Developer experience | `.github/skills/eps-demo-devx/SKILL.md` |
| AI & models | `.github/skills/eps-demo-ai-models/SKILL.md` |
| Cost & security | `.github/skills/eps-demo-cost-security/SKILL.md` |
| Long-lived release readiness | `.github/skills/eps-demo-production-readiness/SKILL.md` |
| Compliance | `.github/skills/eps-demo-compliance/SKILL.md` |
| Repo hygiene | `.github/skills/eps-demo-repo-hygiene/SKILL.md` |

## Repository agents

Use the user-invocable agents under `.github/agents/` when their workflow fits:

- `eps-demo-builder.agent.md` — interviews, builds, deploys, and verifies a demo
  end to end.
- `eps-demo-release-reviewer.agent.md` — read-only readiness audit with an
  evidence-backed release verdict.

## Starting a brand-new demo from this template

If `backend/` and `frontend/` don't exist yet (i.e. this is still
effectively the template — `infra/` always has the baseline resource
group/tags/budget/App Insights guardrails from the template itself, so its
presence alone doesn't mean a demo has been scaffolded), treat the very
first request as a **bootstrap**, not a feature request:

1. **Interview before building.** At minimum, pin down:
   - Partner name (internal use only — never shipped to the public site) and
     the idea/problem being demoed.
   - The core "wow" moment / user journey to optimize for.
   - Likely AI capability (chat, agentic tool use, RAG, generation, etc.), if
     any.
   - Frontend/backend framework preference — otherwise default to the
     recommendations in `eps-demo-architecture` (React + TypeScript;
     Python FastAPI or .NET minimal API; Azure Static Web Apps + Azure
     Functions Flex Consumption, or Azure Container Apps if that doesn't fit).
   - Data needs (none / synthetic / bundled read-only catalog) — real
     partner or customer data is never acceptable (`eps-demo-compliance`).
   - User/job roles and their document, field, tool, and file-access matrix.
   - End-user identity versus agent workload identity, including whether
     different agents need different data-plane rights.
   - Models, Model Router, tool calls, prompt overrides, evidence, telemetry,
     files/PDFs, conversation history, custom domain, and realtime needs.
   - Expected lifetime and audience: one supervised event or a globally shared,
     long-lived demo. The latter loads `eps-demo-production-readiness`.
   - Repository visibility, network restrictions, and local execution context.
     When WSL is requested, the active repo stays in native Linux storage,
     never `/mnt`.
   - Timeline/urgency, since WAF priority defaults to **Cost → Security →
     Performance → Operational Excellence → Reliability**.
2. **Restate the plan**, citing the skills it satisfies (e.g., "per
   `eps-demo-identity`, using the alias+GUID pattern since there's no real
   auth requirement"), before writing code.
3. **Scaffold in this order:** narrative + `docs/` skeleton → `infra/` (Bicep)
   → backend → hosted agents/prompts/tools → frontend → health/telemetry/history
   → `.vscode/` tasks+launch → `.devcontainer/` → CI workflows →
   `config/models.json` (if AI is involved) → `evals/`.
4. Replace this section's premise once the app exists — subsequent requests
   are normal feature work against the rules below.

## Hard rules (no exceptions without explicit human approval)

1. Always hosted in **Azure**. Bicep for IaC.
2. **Managed Identity** always; **no** keys, connection strings, SAS, or passwords in source.
3. **Private Link** to all Azure dependencies. If you knowingly ship without it to move fast, it is a **documented, tracked gap** (see below) — not silent scope creep.
4. **No hardcoded models** — model selection is config-driven.
5. **Content filters on** by default.
6. **No PII collected** — use the alias + GUID local profile pattern for state.
7. **No partner/customer names** on the public site; demo-only indicator visible.
8. **`/docs` is the single source of truth** for documentation.
9. **Coverage gates** in CI: BE ≥ 70%, FE ≥ 60%. `FAKE_AI=1` is mandatory in CI.
10. **VS Code Run-All** task starts the whole stack in split-terminal panels with titles/colors/icons.
11. **Uniform CLI verbs:** `dev`, `test`, `lint`, `deploy` — same in every repo.
12. **No local emulators** — local dev hits a shared dev Azure subscription/resources.
13. **Safe agent visibility** — show progress and tool lifecycle; use only safe
    provider reasoning summaries or application status, never hidden
    chain-of-thought.
14. **Workload identity is explicit** — agents with different downstream data
    rights use different identities/credentials and both positive and negative
    authorization tests.
15. **Long-lived demos are operable** — apply
    `eps-demo-production-readiness` when the demo is globally shared or runs for
    weeks/months.

## Definition of done

A demo is not complete merely because it builds locally. Before handoff:

1. lint, build, tests, coverage, Bicep, and secret checks pass;
2. the intended Azure environment and custom domain are current;
3. the critical live journey and at least one expected denial are verified;
4. health reports ready without scheduled model inference;
5. model/tool/evidence/trace behavior is visible where applicable;
6. narrative and technical docs are served and linked when repository access is
   not guaranteed;
7. temporary deployment resources and packages are removed; and
8. the release commit is pushed and the working tree is clean.

The production-readiness skill owns the detailed version of this contract.

## Ship with an honest gap list, not silent shortcuts

Speed matters more than gold-plating for these demos, so a rule can be
knowingly deferred — but never silently. When you defer one of the hard
rules above (most often Private Link, rate limiting, or CI coverage gates):

- Record it in `docs/README.md`'s standards-compliance table (✅ / ⚠️ / ❌ + link).
- Explain the accepted risk and remediation path in the relevant `docs/security/`
  or `docs/operations/` file.
- Never defer **Managed Identity** (no keys/passwords) or **no PII/no partner
  names** — those two have no "documented gap" escape hatch.

## How to behave

- **Investigate before changing.** Read this file plus the relevant `SKILL.md`(s) before editing.
- **Surface a compliance gap list** before refactoring an existing repo.
- **Ask the human** which gaps to fix in the current pass; do not silently rewrite.
- **Cite the skill** by name in your plan / PR description (e.g., "per `eps-demo-architecture`, switching X to Bicep").
- **Refuse anti-patterns** listed in the skills, even when asked. Propose the compliant alternative.

## Repository-specific overrides

If this specific repo needs to deviate from a standard, capture it as an ADR under `docs/adr/` and link it from the relevant section here. Without an ADR, the skill rule wins.

## Quick commands

```bash
make dev      # run the full stack locally
make test     # run all tests with coverage
make lint     # lint + format check
make deploy   # deploy via Bicep / azd
```
