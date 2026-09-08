# ADR 0007: App Service instead of Static Web Apps + Functions

- Status: accepted
- Date: 2026-09-08
- Context: `eps-demo-architecture` names two compute options — Azure Static Web
  Apps with a BYO Azure Function (Flex Consumption) as the default, or Azure
  Container Apps when that doesn't fit. This demo is neither shape. It is a
  single ~350-line Python standard-library process that fans one question out to
  twelve model deployments in parallel and streams results back over
  Server-Sent Events as each one lands. There is no build step, no package
  manager, and no framework, and that is a deliberate property: the whole point
  of the demo is that a partner can read the scoring logic on screen and believe
  the chart.

  Three things make the default a poor fit:
  - **Long, streaming responses.** A high-reasoning Opus call can run past a
    minute, and the run holds an SSE connection open until the slowest of twelve
    finishes. Consumption-plan request timeouts and buffering are the wrong
    envelope for that.
  - **Nothing to put in Static Web Apps.** The "frontend" is one HTML file
    served by the same process. Splitting it across two services to satisfy the
    shape would add a deployment boundary that buys nothing.
  - **Hostname stability.** This is shown live to partners. Container Apps
    hands out an environment-suffixed FQDN; App Service gives a predictable,
    speakable `*.azurewebsites.net` name. An earlier revision of this demo ran
    on Container Apps and was moved off for exactly this reason.

- Decision: Host on **Linux App Service (B1)** running `python server.py`
  directly, deployed by `azd` as a zip. No container registry and no image
  build — the previous Container Apps revision needed both, and neither earned
  its keep for a dependency-free app.
- Consequences:
  - Good: `azd up` provisions and deploys from a clean clone with no
    registry, no image tag to remember, and no `WEBSITES_PORT` wiring.
  - Good: the web app is named from the azd environment, so the public URL is
    `<environment-name>.azurewebsites.net` — something a presenter can say out
    loud. Picking the environment name picks the hostname.
  - Good: `alwaysOn` keeps the process warm, so the first question of a demo
    isn't paying a cold start in front of an audience.
  - Bad: deviates from the skill's stated compute menu, so anyone reading this
    repo for a template pattern should read this ADR first.
  - Bad: B1 bills continuously rather than per-request. `make down` tears the
    environment down between demos, and the budget alert in `resources.bicep`
    is the backstop.
  - Neutral: **App Service Linux quota is per-region and this subscription has
    none in `eastus2` or `eastus`.** `westus2` works. The cross-region hop to
    the Foundry account in `eastus2` is negligible next to model latency.
