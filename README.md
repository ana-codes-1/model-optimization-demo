# Model Optimization Demo

A live demo to help you choose the right model for your workload.

## The main point

**There is no single "best" model. The right choice depends on what you are optimising for.**

Models differ on four things, and you rarely get to maximise all of them at once:

- **Cost** — what it costs per 1,000 requests
- **Tokens** — how much the model uses to answer
- **Speed** — how long you wait for a response
- **Accuracy** — whether it gets the answer right

This demo measures all four side by side, on the same question, so the trade-offs are
visible instead of assumed.

## How it works

1. Pick a question (or type your own).
2. Click **Run**. Every model configuration answers at the same time, all deployed on
   Azure AI Foundry.
3. Each row shows a **green bar for pass** or a **red bar for fail**, plus tokens, response
   time, and cost per 1,000 requests. Click a row to read the model's actual answer.
4. A model gets up to **three tries**. A cheaper model that needs several attempts to get
   it right may not be saving you anything. You decide whether that is worth it.

Several models appear twice, once at a **base** setting and once at a **frontier** setting
(more thinking), so you can see whether extra reasoning actually helps.

## The hack: questions with a hidden catch

The questions are built so the obvious answer is the wrong one. The thing you need is the
thing that is broken or missing, and models that skim the surface get it wrong.

| Question | What it shows |
|---|---|
| **Car wash** — the car wash is 50 meters away, walk or drive? | The car has to be there to get washed. Does more thinking help? |
| **Dead laptop** — the laptop won't power on; use the self-service portal (4 min) or the service desk (20 min)? | The portal needs a working laptop. Most models miss it. Do you want to optimise for speed or for reasoning? |
| **Shipping compliance** — can 500 laptops ship to two overseas offices? | Almost every model answers, but one refuses. The "best" model may have guardrails you cannot change, which matters if your business needs to ask these questions. |

You can also add a **custom question**. It has to be a two-way choice, because answers are
scored automatically with no judge model.

## What to take away

- A bigger or more expensive model is not automatically a better one for your question.
- More thinking sometimes helps and sometimes only costs more. Test it, don't assume.
- Results vary from run to run. One run is not evidence, so run it more than once.
- Check behaviour such as refusals against your own use case, not just accuracy.

## Run it

Requires Python 3.8+ (no installs) and the Azure CLI, signed in with access to a Foundry
resource.

```bash
cp config.example.json config.json     # set "endpoint" to your resource
az login
python server.py                       # http://localhost:8000
```

Models, questions, and pricing are all set in `config.json`. Adding a model is a config
edit, not a code change.

Deployment, pricing sources, and engineering notes are in [`docs/`](docs/).
