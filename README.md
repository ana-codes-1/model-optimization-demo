# Model Optimization Demo

One trick question, twelve model configurations, measured in parallel. Pass/fail and token
cost land on a live bar chart in about twelve seconds.

The question:

> I want to wash my car. The car wash is 50 meters away. Should I walk or drive?

The answer is **DRIVE** — the car has to physically be at the car wash. Models fixate on
"50 meters is close" and confidently tell you to walk.

## Why this exists

Picking a model by price tier or benchmark leaderboard is guesswork. This measures the
models you can actually deploy, against a question shaped like the ones you actually ask,
and shows what each one costs to get it right — or to get it wrong repeatedly.

Every model appears **twice**: once at its cheapest thinking setting, once at its most
expensive. Pairs sit adjacent in the chart so you compare a model against *itself* and can
answer the only question that matters: **does more thinking help here?**

Often it does not.

## What a run looks like

The committed sample run, in roster order — each model at its cheap setting, then its
expensive one:

| Model | Setting | Result | Attempts | Tokens |
|---|---|---|---|---|
| Claude Opus 5 | effort low | **PASS** | 1 | **153** |
| Claude Opus 5 | effort max | **PASS** | 1 | 279 |
| Claude Haiku 4.5 | thinking off | FAIL | 3 | 360 |
| Claude Haiku 4.5 | thinking 4k | FAIL | 3 | 954 |
| GPT-5.4 nano | effort low | FAIL | 3 | 349 |
| GPT-5.4 nano | effort high | FAIL | 3 | 389 |
| GPT-5.4 mini | effort low | FAIL | 3 | 380 |
| GPT-5.4 mini | effort high | **PASS** | 3 | 796 |
| GPT-5.4 | effort low | FAIL | 3 | 318 |
| GPT-5.4 | effort high | **PASS** | 1 | 210 |
| o3 | effort low | FAIL | 3 | 318 |
| o3 | effort high | **PASS** | 1 | 302 |

Four things fall out of that table:

- **The cheapest row on the board is also correct.** Opus at its *lowest* effort spends 153
  tokens and gets it right — fewer tokens than any failing row spent being wrong.
- **More thinking is not a fix.** Haiku spends 2.6x more with thinking on and returns the
  same wrong answer. Nano's knob moves the cost 11% and changes nothing at all.
- **Sometimes it is a fix.** GPT-5.4 and mini both flip from fail to pass at high effort.
  The knob is worth testing; it is not worth assuming.
- **Watch the attempts column.** `mini-high` passed on its *third* try. A single-shot
  evaluation would have recorded that as either a pass or a fail depending on luck.

**Results are non-deterministic.** Across runs, `o3-low` and `gpt-low` have both flipped
pass/fail. That is a finding, not a bug — it is the argument for measuring rather than
assuming, and for treating any n=1 evaluation with suspicion.

## How it works

```
browser  ──▶  server.py  ──HTTPS──▶  Azure AI Foundry
              (stdlib only)          one resource, N deployments
```

- `server.py` fans all twelve configurations out at once through a `ThreadPoolExecutor`
  and streams each result over SSE the moment it lands, so bars fill in fastest-first.
- Scoring is deterministic. The prompt demands a final line of `ANSWER: WALK` or
  `ANSWER: DRIVE`; the scorer takes the last tag it finds, falling back to an alias table
  so "driving" counts and "driveway" does not. No judge model.
- Retry is adaptive. Pass on the first attempt and it stops. Fail and it tries up to three
  times, accumulating tokens — which is why a stubbornly wrong model looks expensive.
- Auth is Microsoft Entra, not an API key. There are no secrets in this repo to leak.

Every model generation exposes its thinking knob differently, so `config.json` gives each
roster row a raw `params` object that is merged straight into the request body:

```jsonc
{ "id": "opus-high",  "params": { "thinking": { "type": "adaptive" },
                                  "output_config": { "effort": "max" } } }
{ "id": "haiku-high", "params": { "thinking": { "type": "enabled",
                                  "budget_tokens": 4000 } } }
{ "id": "o3-high",    "params": { "reasoning_effort": "high" } }
```

The server knows nothing about what those keys mean. **Adding a model is a config edit,
not a code change.**

## Running it

Requires Python 3.8+ (no pip installs) and the Azure CLI, logged in with access to a
Foundry resource.

```bash
cp config.example.json config.json     # then set "endpoint" to your resource
az login
python server.py                       # http://localhost:8000
```

Edit the `roster` in `config.json` to match your own deployment names.

### Other entry points

```bash
python smoke_test.py                   # run from the CLI, no browser
python verify.py claude-opus-5         # one raw call, complete unfiltered response
```

`verify.py` is the honesty check. It prints the exact URL, the exact body, and Azure's raw
JSON including rate-limit headers — useful when you want to confirm a number rather than
trust one.

### What the dollar figures mean

Each row shows a cost, and the bar can be scaled by cost or by tokens — the toggle sits
next to the Run button. Cost is the better default, because a token axis quietly compares
models whose rates differ by more than 100x: 1,000 nano tokens and 1,000 Opus tokens are
not the same purchase.

The figure on each row is **per 1,000 runs of the question**, not per run. A single run
costs a few thousandths of a cent, and nobody can compare `$0.000094` against
`$0.012345` while talking. At 1,000 runs the same gap reads as **9 cents against $12.35**,
which is the sentence you actually want to say out loud.

The number is **measured tokens × published rate**. The token counts are real — Azure
returns them in every response, split into input and output. The rates live in
`config.json` under `pricing`, in USD per million tokens, and come from two places:

| Models | Rate source | Verifiable? |
| --- | --- | --- |
| GPT-5.4, mini, nano, o3 | Azure Retail Prices API, `serviceName eq 'Foundry Models'`, Global SKU | Yes — `python refresh_prices.py` |
| Claude Opus 5, Haiku 4.5 | Anthropic's published price list | By eye, at the URL the script prints |

That split is not an oversight. Claude has **no token meter in the Azure feed at all** —
on Azure it bills as `claude-consumption-units` rather than per token — so there is no
Microsoft-published per-token rate to look up. Anthropic's list price is the same page the
Foundry portal links to for those models, and it is the best available answer.

`refresh_prices.py` re-pulls every Azure rate and diffs it against `config.json`, exiting
non-zero if anything moved. Run it before a demo if the numbers are going on a slide.

Two things to say out loud if anyone asks how exact these are. Thinking tokens bill as
**output**, which is several times the input rate — that is precisely why the
high-reasoning rows stretch so far. And Azure bills **aggregated daily meters, never
individual requests**, so no per-call invoice exists anywhere to reconcile against. These
are list-price estimates for comparing models against each other, not an invoice.

### Hosting it

The same `server.py` runs locally and in Azure. It picks its credential automatically:
if `IDENTITY_ENDPOINT` is set it uses the platform's managed identity, otherwise it falls
back to whoever is signed in to the Azure CLI. It binds `0.0.0.0` when hosted and
`127.0.0.1` when not, and honours `PORT` and `AZURE_AI_ENDPOINT`.

Deployment is [`azd`](https://aka.ms/azd) over the Bicep in [`infra/`](infra/). The demo is
live at **https://model-optimization-demo.azurewebsites.net**.

```bash
azd auth login

# the azd environment name becomes the hostname: <name>.azurewebsites.net
azd env new model-optimization-demo

# the Foundry account is referenced, not provisioned - see ADR 0008
azd env set AZURE_FOUNDRY_ACCOUNT        <account-name>
azd env set AZURE_FOUNDRY_RESOURCE_GROUP <resource-group>

azd up          # or: make deploy
```

That provisions a resource group, a Linux App Service plan and web app, Log Analytics and
App Insights, and a monthly budget with alerts — then zip-deploys the app. There is no
container image and no registry: the app is standard library only, so App Service runs
`python server.py` directly.

`azd` also grants the two role assignments the demo needs, through a single shared
[`role-assignment.bicep`](infra/modules/role-assignment.bicep) module invoked once for the
web app's identity and once for you. **The Foundry grant is not optional** — that account
sets `disableLocalAuth=true`, so there is no API key to fall back on, and without the role
the app starts fine and then 401s on every model call. Granting the same role to the
signed-in developer is what lets `make dev` reach the real models locally.

The Foundry account itself is *not* provisioned here — it and its twelve deployments
predate this repo. [ADR 0008](docs/adr/0008-existing-foundry-account.md) explains why.
The two `azd env set` values above are deliberately not defaulted in
`infra/main.bicepparam`: the account name is also the endpoint hostname, and this repo
keeps the live endpoint out of source, which is the same reason `config.json` is
gitignored while `config.example.json` carries a placeholder.

Two things that will bite you. **App Service quota is per region**, and this subscription
has none in `eastus2` or `eastus`; `westus2` works. The app does not have to share a region
with the model endpoint — a cross-region hop costs a few tens of milliseconds against calls
that take seconds. And **the plan bills whether or not anyone is using it**:

```bash
make down       # azd down --purge, between demos
```

`docs/adr/0007` records why this is App Service rather than the Static Web Apps + Functions
default in the team standards.

## Adapting it to your own question

The UI has a preset dropdown and editable fields for the question, both answer labels, and
which one is correct. Because scoring is a regex over a fixed option list, a custom
question has to be a **two-way choice**. Anything looser would need a judge model, which
this demo deliberately does not have.

Presets live in `config.json`:

```jsonc
"task": {
  "question": "...",
  "options": ["WALK", "DRIVE"],
  "correct": "DRIVE",
  "why": "The car has to physically be at the car wash."
}
```

### What makes a good question

The shipped presets share one shape: **the thing you need is the thing that is broken or
absent.** A dead laptop cannot open the self-service portal that replaces dead laptops; a
car cannot be washed at a car wash it never travelled to. Surface arithmetic — 4 minutes
beats 20, 50 meters is walkable — points confidently the wrong way.

That second preset separates models far more sharply than the car wash does. In testing,
**10 of 12 configurations chose the portal**, most of them three times in a row. The two
that noticed the laptop was dead were both Claude Opus 5, and the cheaper of the two
settings caught it for fewer tokens than most models spent being wrong.

The third preset is a different shape and worth having for contrast. It asks whether 500
laptops with self-encrypting drives can ship to a customer's Moscow subsidiary, and buries
that inside a larger order that also mentions Shenzhen. Nothing is logically impossible
here — the model has to know that Russia is under export sanctions, that encryption
hardware is controlled, and that only the Moscow leg was actually asked about. It tests
domain knowledge and careful reading rather than a trap, and it scores almost inversely to
the laptop question. Between the two you can show a partner that "which model is best"
has no answer independent of what they intend to ask it.

Avoid famous puzzles. Bat-and-ball and the surgeon riddle are in every training set;
running them here returns 12 of 12 passing on the first attempt, which measures
memorisation rather than reasoning. The useful test is a question shaped like your own
domain, where the wrong answer is the plausible one.

## Files

| File | Purpose |
|---|---|
| `config.example.json` | Endpoint, task, and the roster. The only file most people edit |
| `server.py` | Backend: fan-out, both API transports, scoring, SSE. Standard library only |
| `index.html` | Frontend: chart and controls. No framework, no build step |
| `smoke_test.py` | CLI runner |
| `verify.py` | Single raw call with the full unedited response |
| `refresh_prices.py` | Re-checks the rates in `config.json` against the live Azure price feed |
| `deploy-claude.json` | ARM template for deploying Anthropic models to Foundry |
| `results/` | Every run is archived here as a timestamped JSON file |
| `infra/` | Bicep for `azd up`: App Service, budget, App Insights, and the Foundry role grants |
| `azure.yaml` | `azd` project file — one service, `python server.py` on App Service |
| `Makefile` | The four uniform verbs: `dev`, `test`, `lint`, `deploy` |
| `docs/` | ADRs and the standards-compliance table |
| `AGENTS.md`, `.github/skills/`, `.github/agents/` | Team standards, adopted from `eps-demos-template` |

## Team standards

This repo follows the
[EPS demos template](https://github.com/mcaps-us/eps-demos-template) (Microsoft-internal).
[`AGENTS.md`](AGENTS.md) and the twelve skills under
[`.github/skills/`](.github/skills/) are instructions for coding agents working here —
Copilot reads them before touching anything, so changes arrive shaped like the rest of the
team's demos.

Where this demo deliberately departs from those standards it says so:
[ADR 0007](docs/adr/0007-app-service-for-streaming-fan-out.md) for the compute choice,
[ADR 0008](docs/adr/0008-existing-foundry-account.md) for reusing the Foundry account, and
the [compliance table](docs/README.md) for the rest — including the two rules it knowingly
does not meet (no rate limiting, no CI coverage gates) and why.

The org's ACL, JIT, and compliance-inventory policies were **not** imported. They only
function inside the Microsoft-managed org, and they list team members by alias and email,
which has no business in a public repository.

## Notes on Foundry

Worth knowing if you are rebuilding this:

- OpenAI and Anthropic models sit behind **one** resource and one auth model, but different
  paths and api-versions: `/openai/deployments/{name}/chat/completions` versus
  `/anthropic/v1/messages`. Sending the wrong api-version returns a 404, which is a
  confusing way to learn this.
- With thinking enabled, Anthropic responses put a `thinking` block **before** the `text`
  block. Reading `content[0]` will silently give you the wrong thing.
- Anthropic wants `max_tokens`; OpenAI reasoning models want `max_completion_tokens`.
- Set the token cap generously. Thinking is billed from the same budget, and a tight cap
  truncates the answer to nothing.
