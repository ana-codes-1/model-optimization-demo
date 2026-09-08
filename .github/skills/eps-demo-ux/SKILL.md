---
name: eps-demo-ux
description: UX, accessibility, performance, and visible-quality standards for EPS AI vibe demos. Use when building UI, reviewing pages, or auditing front-end quality.
---

# EPS Demo — UX Standards

## Layout & responsiveness

- Reactive front end, **optimized for desktop landscape**.
- Renders cleanly and **completely** on mobile portrait — no clipped content, no horizontal scroll.
- Dark / light mode toggle in the header.
- For demos with a non-obvious scenario, separate a plain-language Home/About
  narrative, the live demo, and operational health. Link them from desktop and
  mobile navigation.
- Keep secondary information such as history and enforced context in compact,
  collapsed panels when it would displace the primary journey.

## Accessibility

- Standard a11y features (WCAG basics): semantic HTML, keyboard navigation, focus rings, alt text, labeled form fields.
- Color contrast meets WCAG AA.

## Performance

- Performance budget: **FCP < 2s on simulated 4G**, **Lighthouse ≥ 90** on Performance and Accessibility.
- Image assets compressed; no unbounded font/icon downloads.

## Perceived performance & agentic AI streaming

Many of these demos use **agentic AI** that reasons, plans, and calls tools/skills. This takes time and can make the app feel slow or frozen. The UX must make the app feel **alive and working in the background** at every moment.

- **Stream all generative AI to the front end whenever the model/API supports it.** Token-by-token (or chunked) streaming is the default; a blocking request that resolves only when the full answer is ready is an anti-pattern. Fall back to non-streaming only when the underlying service genuinely cannot stream, and say so.
- **Surface safe reasoning summaries or status as it happens.** Use
  provider-authored summaries or application progress so the user can watch the
  agent work. Never expose hidden chain-of-thought.
- **Stream tool/skill calls.** When the agent invokes a tool, skill, search, or sub-agent, show it live (e.g., "Searching catalog…", "Calling stylist agent…", "Checking size guide…") with progress as steps start and complete.
- **Always give a sense of progress.** There must be a visible, continuously-updating signal — streamed text, step list, typing indicator, or animated status — so the app never appears frozen during long-running reasoning.
- **Never block the whole UI on a single long AI call.** Keep the interface responsive; reveal partial results progressively as they arrive.
- **Stream gracefully under failure.** If a stream stalls or errors mid-flight, transition to the designed AI failure / timeout state and preserve whatever partial content already arrived.
- When realtime delivery is added, retain an ordered HTTP streaming fallback,
  deduplicate by sequence, and show the active/fallback state honestly.

## Skeleton screens & loaders

- Use **skeleton screens** for initial page/section loads and **skeleton loaders** for content placeholders (cards, lists, product grids, chat bubbles, panels) wherever it makes sense — instead of bare spinners or blank space.
- Skeletons should **match the shape and layout** of the real content they replace, to minimize layout shift (protect CLS) when content arrives.
- Reserve spinners for short, indeterminate waits; prefer skeletons for content that has a known structure.
- Streamed AI responses should render into a skeleton/placeholder that progressively fills in as tokens arrive.

## State, errors, and recovery

- **Reset Demo** button visible whenever the demo mutates state. Clicking it clears local state and returns to a known starting point.
- Stateful chat also provides **New chat** and **Clear current chat** without
  requiring a full reset. Switching agents starts a clean comparison thread,
  while history preserves which agent produced earlier messages.
- **Designed states** (not framework defaults) for:
  - Empty state
  - Loading state (skeleton screens / skeleton loaders, not bare spinners)
  - AI thinking / streaming state (live reasoning, tool/skill calls, progress)
  - AI failure / timeout (including a mid-stream stall)
  - Rate-limited
  - Auth required (if applicable)

## Governance evidence

When identity/data boundaries are part of the story:

- show the agent-to-identity-to-secret/role-to-data flow in simple language;
- show short principal identifiers and safe portal links, never credentials;
- explain matched, returned, result-limit omitted, field-restricted, citation,
  and denial evidence;
- show requested and actual model, token categories, estimate confidence, and
  trace ID; and
- turn authorized files into an actual browser download through the app. A
  Storage path in answer text is not a download experience.

Long-lived demos add a responsive health page with explicit status semantics,
safe nullable rendering, and a page-level error boundary.

## Internationalization

- Code in an i18n-ready structure (extractable strings, locale wrapper) even if shipped English-only.

## Colophon (mandatory)

Footer must include a colophon block with:

- Last updated date (UTC date is fine)
- Short commit SHA (first 7 chars) linking to the commit on GitHub
- One-line commit message
- A human line: "Last updated **X days ago** — content current as of that date."

The colophon must be generated at build time, not hand-edited.

## Standard footer

- Privacy
- Terms of Service
- About / "How this was built" (links to `/docs/architecture/`)
- Author LinkedIn link(s)
- Link to the GitHub repo when it is public; otherwise link served technical
  documentation that does not require repository access.
- Link to relevant Microsoft product page(s)
- "For demo purposes only" indicator (also visible above the fold)

## Branding posture

- No partner or customer names on the public site.
- Light shared style (header/footer/color tokens) is encouraged; per-demo hero is allowed and expected.
