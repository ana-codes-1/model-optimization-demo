---
name: eps-demo-cost-security
description: Cost optimization and security guardrails for EPS AI vibe demos. Use when provisioning resources, setting up budgets, configuring rate limits, or hardening security.
---

# EPS Demo — Cost & Security Guardrails

## WAF priority (default)

1. Cost Optimization
2. Security
3. Performance
4. Operational Excellence
5. Reliability

Override only if the demo is explicitly built to showcase a different pillar.

## Cost guardrails (mandatory)

- **Subscription / resource-group budget alerts** wired up in Bicep.
- **Hard spend caps** where the resource supports them (e.g., AOAI quotas).
- **Auto-shutdown** of idle resources (Functions Flex scales to zero; Container Apps min replicas = 0).
- **Rate limiting** on any public-facing AI endpoint (per-IP and per-session). Demos must not be cost-bombs when abused.
- Bound request bytes, prompt/override length, stream/event size, tool results,
  mutation frequency, stored records, and file size/expiry.
- Tag every resource: `demo=true`, `owner=<alias>`, `partner=<short-name|none>`, `cost-center=eps-ai-demos`.

## Security guardrails (mandatory)

- **Managed Identity always.** No connection strings, no keys in code, no SAS in source.
- **Key Vault** holds anything that cannot be a Managed Identity (e.g., partner-service creds). RBAC, not access policies.
- External credentials are one-per-security-boundary where possible, with
  downstream least-privilege roles. Validate allowed and forbidden privileges
  before storing them.
- **Private Link** to every Azure dependency.
- Outbound network connects only to Azure services and the named partner service.
- Pin external authorization to one HTTPS origin and disable redirects.
- Use exact custom/default-domain CORS origins; never credentialed wildcard CORS.
- Treat search and source-file access as separate grants. Stage browser-bound,
  expiring downloads rather than exposing Storage credentials or long-lived SAS.
- Content filters on by default (see `eps-demo-ai-models`).
- README + `docs/security/` document the threat model, auth posture, and data flow.

## Things to document

In `docs/cost/`:
- Monthly cost to run today.
- How cost changes at 10x and 100x usage.
- AI service pricing references (link to Azure pricing pages).

In `docs/security/`:
- Threat model.
- Auth choice and rationale.
- Secrets handling.
- Rate limits and abuse mitigations.
- What is logged, where, and how PII is scrubbed.

## Alert hygiene

- Keep cost budgets and service-health alerts separate.
- Alert on actionable sustained conditions such as multiple 5xx responses,
  dependency unavailability, or latency. Document threshold and window.
- Do not alert on `failed requests > 0` without filtering expected client/security
  responses. Normal 400/401/403/404/429 traffic will flap and send both fired and
  resolved email.
- Exercise alert queries without intentionally paging broad recipient lists.

## Anti-patterns to refuse

- Storage account keys in `.env` or app settings.
- Public storage containers.
- Long-lived SAS tokens checked into source.
- AOAI endpoints exposed without rate limiting.
- "We'll add Private Link later."
- A shared broad external API key used by agents with different data rights.
- Telemetry containing prompts, answers, raw tool results, or credentials.
