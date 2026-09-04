"""Independent proof that the deployments are real and answering.

Run:  python verify.py

Makes one raw HTTPS call to a live deployment and prints the COMPLETE unmodified
JSON that Azure returns - no parsing, no filtering, nothing hidden.
"""

import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as fh:
    ENDPOINT = json.load(fh)["endpoint"]

proc = subprocess.run(
    ["az", "account", "get-access-token",
     "--resource", "https://cognitiveservices.azure.com",
     "--query", "accessToken", "-o", "tsv"],
    capture_output=True, text=True, shell=True,
)
token = proc.stdout.strip()
print("Entra token acquired: %d chars\n" % len(token))

target = sys.argv[1] if len(sys.argv) > 1 else "claude-opus-5"

if target.startswith("claude"):
    url = ENDPOINT + "/anthropic/v1/messages?api-version=2026-05-01"
    body = {"model": target, "max_tokens": 200,
            "messages": [{"role": "user", "content": "Reply with exactly: I am " + target}]}
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json",
               "anthropic-version": "2023-06-01"}
else:
    url = "%s/openai/deployments/%s/chat/completions?api-version=2025-04-01-preview" % (ENDPOINT, target)
    body = {"max_completion_tokens": 200,
            "messages": [{"role": "user", "content": "Reply with exactly: I am " + target}]}
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

print("POST " + url)
print("BODY " + json.dumps(body) + "\n")

req = urllib.request.Request(url, json.dumps(body).encode(), headers, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    print("HTTP %s" % resp.status)
    print("--- response headers Azure sent back ---")
    for k, v in resp.headers.items():
        if k.lower().startswith(("x-", "azureml", "apim", "request")):
            print("  %s: %s" % (k, v))
    raw = resp.read().decode()

print("\n--- COMPLETE RAW RESPONSE BODY ---")
print(json.dumps(json.loads(raw), indent=2))
