---
name: eps-demo-docs
description: Documentation structure standard for EPS AI vibe demos. Use when creating docs, writing READMEs, capturing ADRs, or documenting architecture/security/cost/telemetry.
---

# EPS Demo — Documentation

The **`/docs` folder at the repo root is the single source of truth** for all documentation. The README is a short on-ramp that links into `/docs`.

## Required `/docs` structure

```
/docs
├── README.md                # index / map of /docs
├── architecture/
│   ├── overview.md          # what the app does, value, audience
│   ├── diagram.md           # C4 or equivalent diagrams (Mermaid OK)
│   ├── azure-services.md    # what's used and why
│   └── data-flow.md
├── security/
│   ├── threat-model.md
│   ├── auth.md              # chosen identity posture and why
│   ├── secrets.md           # Key Vault, Managed Identity story
│   ├── content-filtering.md
│   ├── rate-limiting.md
│   └── privacy.md           # what is persisted, where, for how long
├── api/                     # optional but recommended
│   └── openapi.yaml
├── cost/
│   ├── cost-to-run.md       # current monthly estimate
│   └── cost-at-scale.md     # how cost changes at 10x/100x usage
├── operations/
│   ├── deploy.md
│   ├── rollback.md
│   └── troubleshooting.md
├── adr/                     # Architecture Decision Records
│   ├── 0001-use-bicep.md
│   ├── 0002-react-vite.md
│   └── ...
├── telemetry/
│   └── events.md            # explicit list of every event the app sends
├── health/
│   └── README.md            # dependency probes, status semantics, caching
├── code-tour.md              # important request paths with current source excerpts
└── build-journal.md         # decisions, dead ends, what worked (optional)
```

## ADR format (keep it tiny)

```
# ADR NNNN: <title>

- Status: accepted | superseded by ADR-XXXX
- Date: YYYY-MM-DD
- Context: 2–4 sentences
- Decision: 1–2 sentences
- Consequences: bullets — both good and bad
```

## Diagrams

- Mermaid in markdown is preferred (renders on GitHub). Use top-to-bottom
  orientation for architecture/security flows, distinctive colors, and bold,
  readable node labels.
- For richer diagrams use Excalidraw and check the `.excalidraw` file in alongside an exported PNG.
- When docs are served as HTML, convert Mermaid to a static SVG/PNG at build
  time; do not rely on a runtime Mermaid renderer. Verify no raw Mermaid source
  remains in generated pages.

## Served documentation

When the repo is private or the audience is nontechnical:

- generate static HTML from canonical Markdown during the application build;
- link Architecture/Network, Security, Code tour, Cost, and Docs home from the
  Home, Demo, and Health footers;
- keep the output responsive and keyboard accessible;
- include official documentation and pricing links for every Azure/external
  service discussed; and
- link the relevant Marketplace/Native ISV offering for partner services.

Write a high-school-readable explanation before technical depth in each key
document. Explain what the component does, why it matters, what proves it works,
and what the demo does not claim.

For private source, embed curated current excerpts in the served code tour. Use
build-time extraction so moved source boundaries fail generation, syntax
highlighting without a public CDN, collapsible/copy controls, and checks that
escaped highlighter markup never renders as text. Never expose credentials or
private configuration in a snippet.

## Telemetry doc

`docs/telemetry/events.md` must enumerate **every event** the app sends, including:

- Event name
- Trigger
- Properties (and whether each property is scrubbed/anonymous)
- Destination (App Insights, Clarity, etc.)

## Linking discipline

- The README has exactly one "Documentation" section that links to `/docs/README.md`.
- All other docs live under `/docs`. Don't scatter `CONTRIBUTING-like` files at the root except the standard ones (`CONTRIBUTING.md`, `CODEOWNERS`, `LICENSE`, `SECURITY.md`).
