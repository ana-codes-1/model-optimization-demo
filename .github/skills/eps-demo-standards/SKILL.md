---
name: eps-demo-standards
description: Master standards for EPS AI partner-facing "vibe-coded" demos. Use whenever you are building, refactoring, or auditing a partner demo web app in this organization. Always invoke this skill first; it points to the focused sub-skills.
---

# EPS AI Vibe Demo — Master Standards

This is the master skill for EPS AI partner demos. It defines the principles and routes Copilot to the focused sub-skills.

## Purpose of these demos

- Help partners envision solutions by shipping a working, tangible web app that showcases the AI features they care about and uses Microsoft AI technologies where applicable.
- A demo is **done** when it has been demo'd to and shared with the partner.

## When to apply

Apply these standards to any partner demo web app maintained by the EPS AI team. New repo or existing — bring the repo into compliance with the rules below.

## Sub-skills (load these as needed)

- `eps-demo-architecture` — Azure architecture, Bicep, hosting, model config
- `eps-demo-ux` — UX, accessibility, performance budget, colophon, reset
- `eps-demo-identity` — auth choices, alias+GUID local profile pattern
- `eps-demo-testing-solid` — SOLID, coverage gates, FAKE_AI, test pyramid
- `eps-demo-docs` — `/docs` folder structure, ADRs, telemetry doc
- `eps-demo-devx` — VS Code tasks, launch.json, devcontainer, uniform CLI
- `eps-demo-ai-models` — config-driven models, content filters, cost surfacing
- `eps-demo-cost-security` — WAF priority, cost caps, Key Vault, rate limits
- `eps-demo-production-readiness` — health, telemetry, alerts, durable state,
  realtime fallback, files, and live release evidence
- `eps-demo-compliance` — GDPR cookie, no PII, "demo only" indicator
- `eps-demo-repo-hygiene` — CI/CD, secret scanning, pre-commit, repo files

## WAF priority (default order)

1. Cost Optimization — these are demos; keep them cheap
2. Security — must demonstrate we don't compromise it
3. Performance — good enough; optimize later
4. Operational Excellence — lightweight for one-off demos; required baseline
   for shared or long-lived demos
5. Reliability — proportional to the demo's lifetime and audience

Override only if a demo is explicitly built to showcase a different pillar.

## Non-negotiables

- Always hosted in Azure.
- Bicep IaC.
- Managed Identity always; no passwords/keys in code.
- Private Link to all Azure dependencies.
- No hardcoded models — model selection is config-driven.
- Content filters on by default.
- Public GitHub repo by default. A private repo is an ADR-backed exception for
  sensitive scenarios; serve the required docs in the app when viewers cannot
  access source.
- `/docs` folder is the single source of truth for documentation.
- VS Code "Run All" task that boots the whole stack with split-terminal panels.
- BE ≥ 70% / FE ≥ 60% coverage gated in CI.
- `FAKE_AI=1` deterministic mode for CI.
- No partner/customer names on the public site; generic, "for demo purposes" indicator visible.
- No PII collected; if state is needed, use the alias+GUID local profile pattern.
- Safe progress/tool visibility only; never expose hidden chain-of-thought.
- Workload identities and data-plane boundaries are explicit and negatively tested.
- Shared or long-lived demos satisfy `eps-demo-production-readiness`.

## Definition of done

The demo is done only when the intended Azure release is live, deterministic
gates pass, the critical journey and denials are verified, health is ready,
documentation is accessible, temporary resources are removed, and the pushed
commit matches the deployed experience. See `eps-demo-production-readiness` for
the full release contract.

## How to use this skill

When asked to "apply EPS demo standards", "audit this demo", or "make this repo compliant":
1. Read this file plus every sub-skill SKILL.md.
2. Read the repo's `AGENTS.md` if present.
3. Produce a compliance gap list against each sub-skill, grouped by sub-skill.
4. Ask the user which gaps to fix in this pass (don't fix all silently).
5. Make changes surgically, one sub-skill area at a time, with brief commits.
