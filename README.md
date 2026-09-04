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

No credentials, then click **Replay** — it renders the committed sample run offline.

### Other entry points

```bash
python smoke_test.py                   # run from the CLI, no browser
python verify.py claude-opus-5         # one raw call, complete unfiltered response
```

`verify.py` is the honesty check. It prints the exact URL, the exact body, and Azure's raw
JSON including rate-limit headers — useful when you want to confirm a number rather than
trust one.

## Adapting it to your own question

Everything is driven by `config.json`:

```jsonc
"task": {
  "question": "...",
  "options": ["WALK", "DRIVE"],
  "correct": "DRIVE",
  "why": "The car has to physically be at the car wash."
}
```

Any two-option question with a defensible right answer works. The interesting ones are
those where the wrong answer is the *plausible* one — that is what separates models.

## Files

| File | Purpose |
|---|---|
| `config.example.json` | Endpoint, task, and the roster. The only file most people edit |
| `server.py` | Backend: fan-out, both API transports, scoring, SSE. Standard library only |
| `index.html` | Frontend: chart and controls. No framework, no build step |
| `smoke_test.py` | CLI runner |
| `verify.py` | Single raw call with the full unedited response |
| `deploy-claude.json` | ARM template for deploying Anthropic models to Foundry |
| `results/sample-run.json` | A real run, committed so Replay works offline |

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
