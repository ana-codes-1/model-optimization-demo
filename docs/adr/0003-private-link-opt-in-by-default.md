# ADR 0003: Private Link opt-in by default, documented gap otherwise

- Status: accepted
- Date: 2026-08-05
- Context: `eps-demo-architecture` lists Private Link to every Azure
  dependency as a "production-grade default, even for tiny scope." In
  practice, standing up a full private-networking stack (VNet, subnets,
  private endpoints, private DNS zones, compute VNet-integration) for a demo
  that might get thrown away in a week is a real speed cost, and the MCAPS
  subscriptions these demos run in often force public network access off by
  policy unless explicitly bypassed. WAF priority for these demos is
  Cost → Security → Performance (`eps-demo-standards`).
- Decision: Data resources default to public network access **with Managed
  Identity + RBAC (never shared keys)**, and Private Link is opt-in per
  resource. When a demo ships without it, that gap must be recorded in this
  demo's `docs/README.md` standards-compliance table and explained in
  `docs/security/threat-model.md` — never a silent shortcut. Managed Identity
  itself has no such escape hatch (see `AGENTS.md`).
- Consequences:
  - Good: first deploy is fast; no VNet plumbing required to get a demo in
    front of a partner.
  - Good: the actual secret-leak risk (shared keys/SAS) is eliminated either
    way, since Managed Identity is never optional.
  - Bad: data-in-transit is reachable over the public internet (auth still
    required) until a demo is hardened — an accepted, documented risk for
    short-lived partner demos, not for anything long-lived or sensitive.
