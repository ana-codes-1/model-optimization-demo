# Documentation

The **`docs/` folder is the single source of truth** for this demo's
documentation, per
[`eps-demo-docs`](../.github/skills/eps-demo-docs/SKILL.md). The root
[README](../README.md) is the on-ramp: what the demo is, how to run it, and
what the dollar figures mean.

This repo adopted the
[`eps-demos-template`](https://github.com/mcaps-us/eps-demos-template) standards
after the app already existed, so `docs/` is deliberately partial: the areas
below that are filled in are filled in honestly, and the ones that are not say
so rather than shipping an empty heading.

## Map

| Area | Contents |
|---|---|
| [adr/](adr/) | Architecture Decision Records, including the two deviations this demo makes |
| architecture/ | Not yet written. The whole app is `server.py` + `index.html`; the README's "How it works" covers the data flow today |
| security/ | Not yet written. Posture summarised in the table below: Managed Identity only, no PII, no stored state |
| cost/ | Not yet written. Per-model cost is a first-class feature of the app itself, and the README's "What the dollar figures mean" documents every rate and its source |
| operations/ | Not yet written. `make deploy` / `make down` and the README's "Hosting it" cover the lifecycle |
| api/ | N/A. The only HTTP surface is `/run` (SSE) and `/config`, both internal to the page |
| telemetry/ | App Insights is provisioned but the app emits no custom events yet |
| health/ | N/A. No health endpoint — this is a supervised demo, not a long-lived service (see the table) |

## Standards compliance at a glance

Honest status against `AGENTS.md`. A rule can be knowingly deferred, never
silently — anything not ✅ has a reason and a route.

| Standard | Status | Notes |
|---|---|---|
| Hosted in Azure | ✅ | Linux App Service, provisioned by [`infra/`](../infra/) |
| Bicep IaC | ✅ | `azd up` builds the whole environment from scratch |
| Managed Identity, no keys | ✅ | System-assigned identity; the Foundry account has `disableLocalAuth=true`, so no key exists to leak even by accident |
| Config-driven models | ✅ | The twelve-model roster, prompts, and price table all live in `config.json`; no model name appears in source |
| Content filters on | ✅ | Foundry defaults, untouched. One preset deliberately trips them — see the README |
| Alias + GUID, no PII | ✅ | No accounts, no state, nothing persisted per user. Runs are written to `results/`, which is gitignored |
| "Demo only" indicator | ⚠️ | The page is self-evidently a model comparison and names no partner, but carries no explicit demo banner |
| `/docs` single source of truth | ⚠️ | This folder plus the ADRs; several areas are still covered by the root README rather than moved here |
| Private Link | ❌ | Deliberate. Public endpoint, no data services, nothing to reach privately — [adr/0003](adr/0003-private-link-opt-in-by-default.md) makes this opt-in |
| Rate limiting | ❌ | **Accepted risk.** The endpoint is public and unauthenticated, and every run spends real tokens. Bounded by the App Service plan, the budget alert below, and `make down` between demos. Fix if this is ever left running unattended |
| CI coverage gates (BE ≥ 70% / FE ≥ 60%) | ❌ | No CI and no unit tests. `make test` runs the roster end to end against Azure and re-verifies every price against the live feed, which is the check that actually protects this demo |
| Budget alerts in Bicep | ✅ | `Microsoft.Consumption/budgets`, 80% actual + 100% forecast, wired to the deployer's email |
| Long-lived production readiness | ❌ | Out of scope by design. This is a supervised, presenter-driven demo; [`eps-demo-production-readiness`](../.github/skills/eps-demo-production-readiness/SKILL.md) applies only if it becomes globally shared |

The two rules with no escape hatch — Managed Identity and no PII / no partner
names — are both ✅.

## Architecture Decision Records

| ADR | Title | Status |
|---|---|---|
| [0001](adr/0001-use-bicep.md) | Use Bicep for IaC | accepted (inherited) |
| [0002](adr/0002-azd-as-deploy-standard.md) | Azure Developer CLI (azd) as the deploy standard | accepted (inherited) |
| [0003](adr/0003-private-link-opt-in-by-default.md) | Private Link opt-in by default, documented gap otherwise | accepted (inherited) |
| [0004](adr/0004-stack-agnostic-template.md) | Template stays stack-agnostic — no prebuilt app or compute | accepted (inherited) |
| [0005](adr/0005-public-repo-by-default.md) | Demo repos are public by default | accepted (inherited) |
| [0006](adr/0006-long-lived-demo-readiness.md) | Long-lived demos require an operational readiness baseline | accepted (inherited) |
| [0007](adr/0007-app-service-for-streaming-fan-out.md) | App Service instead of Static Web Apps + Functions | accepted |
| [0008](adr/0008-existing-foundry-account.md) | Reference the existing AI Foundry account rather than provisioning one | accepted |

0007 and 0008 are this demo's own decisions; both record deviations from
`eps-demo-architecture`, which per `AGENTS.md` is what an ADR is for.
