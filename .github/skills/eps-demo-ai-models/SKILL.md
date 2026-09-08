---
name: eps-demo-ai-models
description: AI and model-handling standards for EPS AI vibe demos — config-driven models, content filters, cost surfacing, evals. Use when calling AI services, surfacing model info, or wiring AI configuration.
---

# EPS Demo — AI & Models

## Configuration-driven (required)

- **No hardcoded model names, endpoints, or deployment IDs** in source.
- A single `models.json` (or equivalent config) at the repo root or under `config/` drives:
  - which models the app uses
  - which deployments map to which logical roles (`chat`, `summarize`, `embed`, etc.)
  - per-model pricing constants for the cost surfacing UI
- Swapping a deprecated model must be a config change, not a code change.

## Content filters

- Azure OpenAI **content filters on by default** (the platform defaults are fine unless the demo has a specific reason).
- Document any deviation in `docs/security/content-filtering.md`.

## Surface model info in the UI

- The UI must indicate which AI **model(s)** are being used right now.
- Where it makes sense for the demo, let end-users **choose a model deployment** from the configured options.
- Indicate which **agents/coding tools** built this demo (e.g., GitHub Copilot, Claude Opus) — in the colophon or About page.

When Model Router is available:

- show it as an explicit configured option, not an unexplained "pinning" toggle;
- display the actual selected inner model from the completed provider response
  body when available;
- do not let a router deployment alias/header overwrite a concrete response
  model; and
- label attribution unavailable rather than inventing an inner model.

Show input, cached-input, output, and reasoning tokens separately. Reasoning
tokens are part of output billing and must not be charged twice. If public
pricing for a routed model is unavailable, retain model/token attribution and
mark the estimate partial or unavailable.

## Agent orchestration and prompts

- Use Microsoft Agent Framework for custom Foundry agent orchestration unless an
  ADR approves another framework.
- Searches, file reads, and business actions are first-class tools with visible
  start/completion/failure events, not hidden helper calls.
- Keep fixed system prompts and request templates in separate files.
- Treat UX instruction overrides as bounded, untrusted presentation guidance
  subordinate to fixed instructions and data-plane authorization.
- Stream only safe provider reasoning summaries or application status. Never
  expose hidden chain-of-thought.
- Project raw tool results to an allowlist of safe counts, IDs, titles,
  citations, denials, and artifact metadata before they cross the trust boundary.
- Explain evidence precisely: authorized matches, returned records, and
  result-limit omissions are not counts of unauthorized records.

## Surface AI cost

- Compute and display the cost of AI calls using the public Azure pricing pulled from `models.json`.
- Show per-interaction cost in the UI when feasible; always show the cost model in `docs/cost/`.

## Evaluations

- Every repo has an `evals/` folder, even if initially empty. This signals intent.
- When evals exist, wire them into CI as a non-blocking check or scheduled job.

## Optional (encourage, don't require)

- Prompt Guards, AI Governance Toolkit integrations.
- An "Explain this answer" affordance that shows model + prompt summary.

## Anti-patterns to refuse

- `client = AzureOpenAI(model="gpt-4-...")` literal anywhere outside config loading.
- AI calls that bypass the model-routing layer.
- Cost numbers hardcoded as magic literals.
- Router aliases presented as the actual selected model.
- Prompt wording used as the only data-authorization control.
- Raw tool output or hidden chain-of-thought sent to the browser.
