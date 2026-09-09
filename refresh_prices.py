"""Re-check the rates in config.json against the Azure Retail Prices API.

Run this before a demo. It answers the only honest question you can ask about the
dollar figures on the chart - "are these still the published rates?" - by pulling
them again from the public feed and diffing.

    python refresh_prices.py

It never edits config.json. It prints what changed and exits non-zero if anything
drifted, so you can decide what to do about it.

What it cannot check: Claude. Anthropic models have no token meter in the Azure
feed at all - they bill as consumption units - so those rates come from Anthropic's
published price list and have to be eyeballed at the URL printed below.
"""

import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://prices.azure.com/api/retail/prices"
REGION = "eastus2"
ANTHROPIC_PRICES = "https://platform.claude.com/docs/en/about-claude/pricing"

# The meter behind each rate. Global-deployment SKUs, which is what this demo uses.
# Values are (input meter, output meter, cached-input meter, per-how-many-tokens).
METERS = {
    "gpt-5.4":      ("5.4 inp Gl 1M Tokens", "5.4 opt Gl 1M Tokens",
                     "5.4 cd inp Gl 1M Tokens", 1_000_000),
    "gpt-5.4-mini": ("5.4 mini Inp Gl 1M Tokens", "5.4 mini Opt Gl 1M Tokens",
                     "5.4 mini cd Inp Gl 1M Tokens", 1_000_000),
    "gpt-5.4-nano": ("5.4 nano Inp Gl 1M Tokens", "5.4 nano Opt Gl 1M Tokens",
                     "5.4 nano cd Inp Gl 1M Tokens", 1_000_000),
    "o3":           ("o3 0416 Inp glbl Tokens", "o3 0416 Outp glbl Tokens",
                     "o3 0416 cached Inp glbl Tokens", 1_000),
    "MAI-Thinking-1": ("MAI-Thinking-1 Inp glbl 1M Tokens",
                       "MAI-Thinking-1 Opt glbl 1M Tokens",
                       "MAI-Thinking-1 Cd Inp glbl 1M Tokens", 1_000_000),
    # xAI publishes no cached-input meter, so that field is unverifiable and
    # config.json mirrors the input rate rather than inventing a discount.
    "grok-4-1-fast-reasoning": ("Grok 4.1 Inp Glbl Tokens",
                                "Grok 4.1 Outp Glbl Tokens", None, 1_000),
    # These two are deployed GlobalStandard but only DataZone meters are
    # published, so this checks the closest figure that exists, not the exact one.
    "Kimi-K2.6":    ("FW Kimi K2.6 Inp DZ Tokens", "FW Kimi K2.6 Outp DZ Tokens",
                     "FW Kimi K2.6 Cache Inp DZ Tokens", 1_000),
    "DeepSeek-V4-Flash": ("FW Deepseek-v4-Flash In DZ Tokens",
                          "FW Deepseek-v4-Flash Opt DZ Tokens",
                          "FW Deepseek-v4-Flash Cd In DZ Tokens", 1_000),
}


def fetch(meter):
    """Return the consumption retail price for one meter in REGION, or None."""
    flt = ("serviceName eq 'Foundry Models' and armRegionName eq '%s' and meterName eq '%s'"
           % (REGION, meter.replace("'", "''")))
    url = BASE + "?" + urllib.parse.urlencode({"$filter": flt,
                                               "api-version": "2023-01-01-preview"})
    with urllib.request.urlopen(url, timeout=60) as resp:
        items = json.load(resp).get("Items", [])
    prices = {i["retailPrice"] for i in items if i.get("type") == "Consumption"}
    if len(prices) != 1:
        return None  # missing, or ambiguous - either way, do not guess
    return prices.pop()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cfg = json.load(open(os.path.join(here, "config.json"), encoding="utf-8"))
    pricing = cfg.get("pricing") or {}

    drift = 0
    print("Checking Azure-metered rates against the live retail feed (%s)\n" % REGION)
    for model, (m_in, m_out, m_cached, per) in METERS.items():
        have = pricing.get(model)
        if not have:
            print("  %-16s not in config.json - skipped" % model)
            continue
        for field, meter in (("in", m_in), ("out", m_out), ("cached_in", m_cached)):
            if meter is None:
                print("  %-16s %-10s no meter published - not checkable" % (model, field))
                continue
            live = fetch(meter)
            if live is None:
                print("  %-16s %-10s METER NOT FOUND: %s" % (model, field, meter))
                drift += 1
                continue
            live_per_million = live * (1_000_000 / per)
            mine = have.get(field)
            if mine is None:
                continue
            if abs(live_per_million - mine) < 1e-9:
                print("  %-16s %-10s $%-9s ok" % (model, field, mine))
            else:
                print("  %-16s %-10s $%-9s CHANGED -> $%s"
                      % (model, field, mine, live_per_million))
                drift += 1

    print("\nNot checkable here - no Azure token meter exists for these:")
    for model, rate in pricing.items():
        if rate.get("source") == "anthropic-list":
            print("  %-16s in $%-6s out $%-6s  verify at %s"
                  % (model, rate["in"], rate["out"], ANTHROPIC_PRICES))

    if drift:
        print("\n%d rate(s) drifted. Update config.json before quoting these numbers." % drift)
    else:
        print("\nAll Azure-metered rates match the published feed.")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
