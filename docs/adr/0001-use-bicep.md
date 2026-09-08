# ADR 0001: Use Bicep for IaC

- Status: accepted
- Date: 2026-08-05
- Context: `eps-demo-architecture` mandates Bicep as the IaC standard — no
  Terraform, no hand-written ARM JSON — so every demo's infrastructure is
  readable and reviewable the same way.
- Decision: All infrastructure lives under `infra/` as Bicep, with a
  subscription-scoped `main.bicep` (creates the resource group) calling a
  resource-group-scoped `resources.bicep`.
- Consequences:
  - Good: one IaC language across every EPS demo; `az bicep build` validates
    templates in CI with no extra tooling.
  - Good: subscription scope lets `azd up` bring up an environment from
    absolute scratch — no manually pre-created resource group.
  - Bad: architects who know Terraform better have a small ramp-up cost.
