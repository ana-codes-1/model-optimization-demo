# ADR 0004: Template stays stack-agnostic — no prebuilt app or compute

- Status: accepted
- Date: 2026-08-05
- Context: `eps-demo-architecture` recommends but does not mandate a
  frontend/backend framework, and partner ideas vary widely enough that
  presupposing one stack (or one compute shape) would mean ripping it out on
  many demos. Early drafts of this template provisioned Static Web Apps +
  Azure Functions + AI Foundry directly in `infra/`, which baked in a compute
  and AI opinion nothing had asked for yet.
- Decision: This template ships no `backend/`, `frontend/`, or compute/data
  resources. `infra/` only wires what's true regardless of stack: the
  resource group, tags, a budget, and App Insights/Log Analytics. The
  `/new-demo` bootstrap flow interviews the architect and adds the actual
  stack, compute, and data services per demo.
- Consequences:
  - Good: no dead code or wrong-shaped resources to strip out of every demo.
  - Good: architects genuinely choose React/Vue, .NET/Python/Node, SWA+Functions/
    Container Apps, etc. per partner idea, per `eps-demo-architecture`.
  - Bad: there is no working "hello world" to smoke-test the toolchain before
    the first real demo — first-run validation happens on the first real
    build instead.
