---
name: eps-demo-devx
description: Developer experience standards for EPS AI vibe demos — VS Code tasks, launch.json compound debug, devcontainer, uniform CLI. Use when setting up `.vscode/`, devcontainer, or local dev ergonomics.
---

# EPS Demo — Developer Experience

## Goal

A new architect can `git clone`, open in VS Code, press one key (or run "Run All"), and have the entire stack running with debuggers attached. No README archaeology.

## Uniform repo CLI (required)

Every demo exposes the same top-level commands regardless of language/stack. Pick the wrapper that fits (npm scripts, Makefile, Just), but the commands are fixed:

- `dev` — run the full stack locally
- `test` — run all tests with coverage
- `lint` — lint + format check
- `deploy` — deploy via Bicep/azd

VS Code tasks wrap these. Don't duplicate logic in tasks.json.

## VS Code tasks (`.vscode/tasks.json`)

- One task per service (e.g., `frontend`, `backend-api`, `functions`).
- Each task runs in its **own dedicated terminal**, configured with:
  - `presentation.panel: "dedicated"`
  - `presentation.group: "stack"` (so they share a split group)
  - **Distinct title, color, and icon per service** (e.g., 🟦 Frontend, 🟧 Backend, 🟩 Functions)
- A compound task named **"Run All"** starts every service in parallel, split side-by-side.

Skeleton:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "frontend",
      "type": "shell",
      "command": "npm run dev --workspace=frontend",
      "isBackground": true,
      "presentation": {
        "panel": "dedicated",
        "group": "stack",
        "reveal": "always"
      },
      "icon": { "id": "browser", "color": "terminal.ansiBlue" }
    },
    {
      "label": "backend-api",
      "type": "shell",
      "command": "npm run dev --workspace=backend",
      "isBackground": true,
      "presentation": {
        "panel": "dedicated",
        "group": "stack",
        "reveal": "always"
      },
      "icon": { "id": "server-process", "color": "terminal.ansiYellow" }
    },
    {
      "label": "Run All",
      "dependsOn": ["frontend", "backend-api"],
      "dependsOrder": "parallel",
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}
```

## Launch configurations (`.vscode/launch.json`)

- One config per debuggable service.
- A **compound** named "Debug All" that launches every service with breakpoints working. F5 should "just work".

## Devcontainer / Codespaces (required)

- `.devcontainer/devcontainer.json` provides the full toolchain: Node, Python or .NET, Azure CLI, Bicep, GitHub CLI.
- Post-create runs `npm install` (or equivalent) and a smoke check.
- A user with no local tools should be productive via Codespaces.

## Local cloud dependencies

- **No emulators.** Local dev points at a shared dev Azure Storage account (and Cosmos/SQL/Foundry as needed) via Managed Identity or short-lived credentials.
- Document the dev resource names and how to get access in `docs/operations/`.

## WSL and authentication

- When a user chooses WSL, clone and work in the native Linux filesystem (for
  example `~/src/demo`), never under `/mnt`, to avoid filesystem/watch/build
  performance problems.
- Verify `az`, `azd`, and `gh` authentication from the same shell and user that
  will build and deploy before provisioning anything.
- If GitHub CLI has multiple accounts, select the account authorized for the
  target org and verify SSO/EMU access. Do not treat a different account's login
  as proof.
- Keep complex WSL shell logic in scripts or safely encoded commands; host-shell
  interpolation can corrupt `$variables`, JSON, and query syntax.
- Document any VNet-connected deployment runner, and automate/verify deletion of
  its identity, roles, packages, and artifact container after use.

## Recommended VS Code extensions (`.vscode/extensions.json`)

- `ms-azuretools.vscode-bicep`
- `ms-azuretools.vscode-azurefunctions` (if Functions)
- `github.copilot`, `github.copilot-chat`
- Stack-specific linters/formatters.

## Optional

- Storybook for the shared component library only.
