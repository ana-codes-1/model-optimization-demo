---
name: eps-demo-production-readiness
description: Operational readiness standards for EPS AI demos shared globally or run for weeks or months. Use when adding health, telemetry, alerts, durable history, realtime delivery, file downloads, or release gates.
---

# EPS Demo - Production Readiness

This skill defines the minimum operational contract for a demo that will outlive
one supervised presentation. It does not turn a demo into a production service;
it makes the demo honest, supportable, and safe to share.

## When this skill is required

Apply every section when a demo is:

- shared with multiple presenters or a global audience;
- expected to run unattended for more than one event;
- connected to live AI, external data, files, or paid services; or
- used to demonstrate production governance, security, or observability.

For a one-off supervised demo, explicitly mark deferred items in the standards
table and operations docs. Identity, secret hygiene, synthetic data, and honest
disclosure are never deferrable.

## Completion contract

A long-lived demo is not complete until:

1. the intended Azure environment is deployed;
2. deterministic lint, build, tests, and coverage gates pass;
3. the critical live journey succeeds through the public application boundary;
4. expected authorization denials are proven, not inferred from answer wording;
5. `/health` reports ready from the deployed origin;
6. model, tool, evidence, token, and trace data are visible where applicable;
7. narrative and technical documentation are served and linked from the app;
8. temporary runners, identities, role assignments, packages, and test artifacts
   are removed; and
9. the release commit is pushed and the working tree is clean.

## Health surface

Long-lived demos expose both a human `/health` page and a machine-readable health
endpoint.

- Use explicit states such as `healthy`, `available`, `configured`, `degraded`,
  `unreachable`, and `misconfigured`. Explain what each state proves.
- Probe the actual dependency path with managed identity where safe.
- Hosted-agent readiness uses an authenticated, intentionally invalid request
  that starts the container and exercises startup authorization but stops before
  model inference.
- Include negative probes where denial is a security requirement. A 403 is
  healthy only when the probe proves the exact expected authorization denial,
  not a firewall, DNS, or authentication failure.
- Cache and coalesce expensive probes. Browser polling must not run more often
  than the server cache and must pause while the tab is hidden.
- Never centralize agent credentials in the health service. Never return secret
  values, tokens, full principal IDs, private endpoints, or raw downstream errors.
- Render nullable probe data safely and use a page-level error boundary so one
  bad field cannot blank the dashboard.

## Agent streaming and transport

- Stream progress, safe provider reasoning summaries, tool start/completion,
  answer deltas, model attribution, usage, completion, and errors.
- Never expose hidden chain-of-thought. If the provider supplies no safe summary,
  show concise application-authored status instead.
- Use monotonically increasing sequence numbers. Deduplicate and reorder events
  when more than one transport can deliver them.
- A realtime service such as SignalR may reduce latency, but ordered HTTP NDJSON
  remains an explicit fallback. A realtime failure must not fail an otherwise
  healthy answer.
- Bind realtime channels to unguessable session context. Use exact HTTPS CORS
  origins for default and custom domains; never use `*` with credentials.
- Bound connection negotiation, publication, total streaming time, event size,
  and tool argument/result projections.

## Authorization and evidence

- Keep user identity and agent workload identity separate.
- For agents with different data boundaries, use one workload identity and one
  downstream credential/role per boundary.
- Show authorized matches, returned records, result-limit omissions, citations,
  field restrictions, and denials in simple language.
- Unauthorized records removed by DLS do not appear in counts. Do not label
  result-limit omissions as security-withheld records.
- Raw tool output stays inside the trusted backend/agent process. Public events
  use an allowlist of safe IDs, titles, counts, statuses, and artifact metadata.

## Durable history and file artifacts

When a public demo needs browser-scoped continuity without user authentication:

- generate a random GUID in local storage and disclose that it is a lookup handle,
  not authentication;
- hash the GUID before using it as a cloud-storage partition;
- persist which agent produced every conversation;
- use strong ETags for updates/deletes and return conflicts instead of silently
  overwriting concurrent changes;
- cap request size, nested fields, messages, artifacts, mutations, per-browser
  conversations, and global stored objects;
- configure retention/lifecycle deletion; and
- provide New chat and Clear current chat independently of Reset Demo.

Files use a separate authorization path from search:

- read only from workload-authorized source containers;
- stage random-ID, browser-bound download artifacts;
- enforce content type, size, hash, and short application expiry;
- use Storage lifecycle cleanup as defense in depth; and
- stream through the application without exposing a key or SAS URL.

## Observability and alerts

- Use one W3C trace ID across browser evidence, API, hosted agent, tools, Azure
  Monitor, and any approved secondary sink.
- Telemetry records operational facts only. Exclude prompts, answers, reasoning
  text, search terms, raw documents, tool-result bodies, files, credentials, full
  principal IDs, and private invocation URLs.
- Give telemetry ingestion a dedicated write-only credential and readers a
  separate read-only role. Never reuse retrieval credentials.
- Alerts must be actionable. Do not page on every failed request: expected 4xx
  security responses and isolated user errors will flap and generate paired
  fired/resolved email floods. Prefer sustained 5xx, availability, latency, or
  dependency-failure conditions with a documented window and threshold.
- Keep budget alerts separate from service-health alerts.

## Release and cleanup

Before handoff:

- verify the custom domain as well as the default hostname;
- verify at least one direct model and one routed-model call when both exist;
- test one positive and one negative data/file boundary;
- query the resulting trace in every documented telemetry destination;
- verify generated documentation, diagrams, and source viewers render;
- verify portrait-mobile layout has no clipped content or horizontal page scroll;
- reconcile portal links and short principal metadata with active deployments;
- run a credential scan; and
- delete all temporary deployment resources and local packages.

## Anti-patterns to refuse

- Treating a configured endpoint as a live health check.
- Health probes that invoke paid models on a schedule.
- Alerting on `failed requests > 0` without excluding expected client responses.
- Realtime delivery with no ordered fallback.
- Conversation storage with wildcard/weak ETags or unlimited growth.
- Returning a file path instead of an authorized download.
- Logging prompts, answers, tool bodies, or credentials for convenience.
- Claiming completion after local tests while the deployed route is stale.
