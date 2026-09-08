# ADR 0006: Long-lived demos require an operational readiness baseline

- Status: accepted
- Date: 2026-08-28
- Context: Some EPS demos are used once under direct supervision; others are
  shared globally for weeks or months. The latter need health, bounded state,
  actionable alerts, safe telemetry, and live release evidence without being
  represented as production services.
- Decision: Apply `eps-demo-production-readiness` to every shared or long-lived
  demo. One-off demos may document deferred operational items, but identity,
  secret hygiene, synthetic data, and honest disclosure remain mandatory.
- Consequences:
  - Good: future demos ship with supportable health, telemetry, alert, history,
    and cleanup contracts.
  - Good: "done" includes the deployed experience and authorization evidence,
    not only local tests.
  - Bad: long-lived demos require more implementation and validation than a
    supervised prototype.
  - Bad: teams must maintain explicit gap documentation when they choose the
    lighter one-off path.
