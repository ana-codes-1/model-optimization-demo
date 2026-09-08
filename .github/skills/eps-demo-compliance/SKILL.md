---
name: eps-demo-compliance
description: Legal, compliance, and privacy standards for EPS AI vibe demos. Use when adding cookie banners, privacy text, user-facing data collection, or generating synthetic data.
---

# EPS Demo — Compliance, Legal, Privacy

## Visible posture

- **GDPR cookie acknowledgement** on first visit. Functional/strictly-necessary by default; analytics opt-in.
- **"For demo purposes only"** indicator visible above the fold (not just in the footer).
- **No partner or customer names** anywhere on the public site. Keep the surface generic so the repo can be public.

## Data collection rules

- **No PII.** Do not ask for name, email, phone, address, or any identifying information.
- If the demo needs personalization or state per "user", use the alias + GUID local profile pattern from `eps-demo-identity`.
- Only the **GUID** ever leaves the browser to identify a user record in cloud storage.

## Synthetic data (when approximating a partner platform)

- All sample data must be **synthetic**. Never scrape or import real customer data.
- Document the synthetic-data generation method in `docs/security/privacy.md` (or a dedicated `docs/data/synthetic.md`).
- Avoid look-alike data that could be mistaken for a real organization's records.
- Synthetic PII may appear only when an intentional legacy/negative scenario
  needs to prove field filtering. Make it obviously fake, label the path as
  intentionally unsafe, and ensure governed identities cannot retrieve it.

## Telemetry and model safety

- Do not record prompt text, answer text, provider reasoning, search terms, raw
  documents, tool-result bodies, file contents, credentials, full workload
  principal IDs, or private invocation URLs.
- Safe operational metadata includes event type, status, duration, model ID,
  token counts, result counts, short non-secret prefixes, and trace IDs.
- Provider reasoning summaries are shown only when explicitly safe for display;
  hidden chain-of-thought is never collected or exposed.

## Legal text

The footer must include:

- Privacy notice that states: no PII collected; alias and GUID stored only in browser; analytics (if any) is anonymous.
- Terms of Service / disclaimer: "This is a demonstration. Not for production use. No warranty. Provided as-is. Not an official Microsoft product."
- Link to the source repo on GitHub.

## Sensitive scenarios

- If the demo would expose partner IP, sensitive data, or forward-looking strategy, **gate it with auth** (see `eps-demo-identity`) and keep the repo private.
- If unsure, default to private repo + auth gate, then loosen after review.
- Public remains the normal posture for synthetic reusable demos. When a private
  repo is justified, serve the audience-facing docs from the app so security and
  cost explanations do not depend on source access.
