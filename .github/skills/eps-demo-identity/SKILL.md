---
name: eps-demo-identity
description: Identity and auth standards for EPS AI vibe demos. Use when adding sign-in, user profiles, personalization, or any state that needs to identify a "user".
---

# EPS Demo — Identity & Auth

Choose the **lightest** option that meets the demo's needs.

## Decision matrix

| Scenario | Choose |
|---|---|
| Public, generic, no IP, no state per user | **No auth** |
| Personalization or state per "user", but no real identity needed | **Local alias + GUID profile** (default for state demos) |
| Partner IP, sensitive data, forward-looking strategy | **Auth gate** — Azure SWA built-in (GitHub) or Entra (external directory pattern TBD as a team) |

## The alias + GUID local profile pattern (default for stateful demos)

When a demo needs "users" for personalization or state management but does **not** need real identity:

1. On first visit, generate a random **alias** (e.g., "Curious Otter 4821") and a **GUID v4**.
2. Store both in **browser local storage**.
3. **Only the GUID** is sent to cloud services as the user identifier.
4. **Never collect** name, email, phone, address, or any PII.
5. Provide a "Reset profile" control near the Reset Demo button.

If the GUID indexes cloud state, hash it before constructing a storage partition.
Use strong ETags for updates/deletes, return conflicts instead of overwriting,
and cap payload size, mutations, records per GUID, total records, and retention.
State clearly that a browser GUID is a lookup handle, not authentication.

A shared React component implementing this pattern lives under `packages/alias-profile/` when included. If absent in the repo, scaffold it locally and contribute it back later.

## Auth gates

- **Azure SWA built-in auth (GitHub provider)** is the lightest gated option. Works when test users are developers.
- **Entra ID with external directory** for non-GitHub test users — pattern is being defined as a team standard. Don't invent a one-off; flag it for team discussion if needed.

## Always

- Document the chosen auth posture in `docs/security/`.
- Document what is persisted, where, and for how long, in `docs/telemetry/` (alongside event list).

## Agent workload identity

End-user identity and agent workload identity are separate decisions. A public
demo may have no signed-in user while each hosted agent still has its own Entra
identity.

When agents have different downstream rights:

1. use one runtime identity per security boundary;
2. capture the platform-created runtime principal after deployment;
3. assign `Key Vault Secrets User` at one exact secret scope, not vault,
   resource-group, or subscription scope;
4. assign file/container RBAC independently from search access;
5. prove the own secret/container succeeds and every sibling boundary returns
   the exact expected denial; and
6. rerun reconciliation whenever an immutable agent version changes identity.

Inside the hosted process, use `DefaultAzureCredential`. The platform supplies
the identity; the credential obtains its token. Key Vault evaluates the token's
`oid` claim against RBAC. Do not pass the object ID as a credential or embed it
in runtime code.

For a downstream service that requires API keys, Entra brokers access to the
Key Vault secret; the downstream key's own role enforces its data permissions.
Document this honestly. DLS, FLS, tool permission, and source-file permission
are independent controls and should remain visible as such.
