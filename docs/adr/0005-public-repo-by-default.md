# ADR 0005: Demo repos are public by default

- Status: accepted
- Date: 2026-08-05
- Context: `eps-demo-compliance` says to default to a private repo when
  unsure, but also requires no PII, no partner/customer names, and a visible
  "for demo purposes only" indicator on anything public — i.e., the standard
  posture is already designed to be safe to publish. The whole point of these
  demos is a shareable asset the partner (and Microsoft) can point to.
- Decision: New demo repos default to **public** visibility. A repo is kept
  private only when it would expose partner IP, sensitive data, or
  forward-looking strategy — in which case it should also be gated with auth
  (`eps-demo-identity`), per the compliance skill's sensitive-scenarios
  guidance.
- Consequences:
  - Good: demos are shareable by default with no extra step; the GitHub source
    link in the footer (`eps-demo-ux`) just works.
  - Good: forces real discipline on no-PII/no-partner-names from the start,
    rather than as a late "make it public" scramble.
  - Bad: a repo built without this ADR in mind could leak something sensitive
    if an architect forgets to flag a sensitive scenario — mitigated by the
    compliance skill's explicit call to default private when unsure.
  - Neutral: when a private repo is justified, audience-facing architecture,
    security, code-tour, and cost docs are served from the app instead of
    depending on repository access.
