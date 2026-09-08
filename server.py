"""Model optimization demo: one question, twelve deployments, pass/fail + tokens.

Stdlib only. Run:  python server.py   ->  http://localhost:8000
"""

import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(ROOT, "results")

# config.json is gitignored because it carries a real endpoint, so a fresh clone
# (and `azd up`, which deploys from the working tree) falls back to the committed
# example. Everything except the endpoint is identical between the two, and
# AZURE_AI_ENDPOINT below supplies the endpoint in Azure.
CONFIG_PATH = os.path.join(ROOT, "config.json")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(ROOT, "config.example.json")

with open(CONFIG_PATH, encoding="utf-8") as fh:
    CFG = json.load(fh)

# Lets the hosted build ship a placeholder config and inject the real endpoint.
if os.environ.get("AZURE_AI_ENDPOINT"):
    CFG["endpoint"] = os.environ["AZURE_AI_ENDPOINT"].rstrip("/")

if "YOUR-FOUNDRY-RESOURCE" in CFG["endpoint"]:
    raise SystemExit(
        "No AI endpoint configured. Either copy config.example.json to config.json "
        "and set \"endpoint\", or set the AZURE_AI_ENDPOINT environment variable."
    )


def _build_commit():
    """Which commit is actually serving. Read from .git directly rather than
    shelling out, because the deployed App Service image has no git binary."""
    env = os.environ.get("BUILD_COMMIT")
    if env:
        return env[:7]
    try:
        with open(os.path.join(ROOT, ".git", "HEAD"), encoding="utf-8") as fh:
            head = fh.read().strip()
        if head.startswith("ref: "):
            with open(os.path.join(ROOT, ".git", head[5:]), encoding="utf-8") as fh:
                head = fh.read().strip()
        return head[:7]
    except OSError:
        return None


BUILD_COMMIT = _build_commit()


def build_prompt(task):
    """Force a tagged final line so scoring stays deterministic for any question."""
    tags = " or ".join("ANSWER: " + o for o in task["options"])
    return (task["question"] + "\n\n"
            + "Answer in one or two sentences, then end with a final line exactly: "
            + tags)

_token = {"value": None, "fetched": 0.0}
_token_lock = threading.Lock()
RESOURCE = "https://cognitiveservices.azure.com"


def _token_from_managed_identity():
    """Container Apps injects these two vars. Returns None when running locally."""
    endpoint = os.environ.get("IDENTITY_ENDPOINT")
    header = os.environ.get("IDENTITY_HEADER")
    if not (endpoint and header):
        return None
    url = "%s?resource=%s&api-version=2019-08-01" % (endpoint, RESOURCE)
    req = urllib.request.Request(url, headers={"X-IDENTITY-HEADER": header})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)["access_token"]


def _token_from_cli():
    """Local path: borrow whoever is signed in to the Azure CLI."""
    proc = subprocess.run(
        ["az", "account", "get-access-token",
         "--resource", RESOURCE, "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, shell=True,
    )
    value = proc.stdout.strip()
    if not value:
        raise RuntimeError("az token fetch failed: " + proc.stderr.strip()[:200])
    return value


def get_token(force=False):
    """Entra token. The resource has disableLocalAuth=true, so there is no API key."""
    with _token_lock:
        stale = time.time() - _token["fetched"] > 1800
        if force or stale or not _token["value"]:
            _token["value"] = _token_from_managed_identity() or _token_from_cli()
            _token["fetched"] = time.time()
        return _token["value"]


def _post(url, body, extra_headers=None, retry_on_401=True):
    headers = {"Authorization": "Bearer " + get_token(), "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, json.dumps(body).encode(), headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=CFG["timeout_seconds"]) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        if err.code == 401 and retry_on_401:
            get_token(force=True)
            return _post(url, body, extra_headers, retry_on_401=False)
        raise RuntimeError("HTTP %s: %s" % (err.code, err.read().decode()[:200]))


def call_openai(entry, prompt):
    url = "%s/openai/deployments/%s/chat/completions?api-version=%s" % (
        CFG["endpoint"], entry["deployment"], CFG["openai_api_version"])
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": CFG["openai_max_completion_tokens"],
    }
    body.update(entry.get("params", {}))
    data = _post(url, body)
    usage = data.get("usage", {})
    details = usage.get("prompt_tokens_details") or {}
    return {
        "text": (data["choices"][0]["message"].get("content") or "").strip(),
        "tokens": usage.get("total_tokens", 0),
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "tokens_cached": details.get("cached_tokens", 0) or 0,
        "thinking": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
    }


def call_anthropic(entry, prompt):
    url = "%s/anthropic/v1/messages?api-version=%s" % (
        CFG["endpoint"], CFG["anthropic_api_version"])
    body = {
        "model": entry["deployment"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": CFG["anthropic_max_tokens"],
    }
    body.update(entry.get("params", {}))
    data = _post(url, body, {"anthropic-version": CFG["anthropic_version_header"]})
    usage = data.get("usage", {})
    # When thinking is on, a `thinking` block precedes the `text` block.
    text = " ".join(b.get("text", "") for b in data.get("content", [])
                    if b.get("type") == "text").strip()
    return {
        "text": text,
        "tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        "tokens_in": usage.get("input_tokens", 0),
        "tokens_out": usage.get("output_tokens", 0),
        "tokens_cached": usage.get("cache_read_input_tokens", 0) or 0,
        "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens", 0),
    }


def cost_usd(entry, tokens_in, tokens_out, tokens_cached):
    """List-price estimate. None when we have no defensible rate for the model.

    Thinking tokens are already inside tokens_out on both APIs, and they bill as
    output - which is the whole point of showing this next to the pass/fail.
    """
    rate = (CFG.get("pricing") or {}).get(entry["deployment"])
    if not rate:
        return None
    billable_in = max(tokens_in - tokens_cached, 0)
    cached_rate = rate.get("cached_in", rate["in"])
    return (billable_in * rate["in"]
            + tokens_cached * cached_rate
            + tokens_out * rate["out"]) / 1_000_000


def score(text, task):
    """Deterministic. Prefer the tagged final line; fall back to first bare mention."""
    text = text or ""
    options = task["options"]
    tag = re.compile(r"ANSWER:\s*\**\s*(" + "|".join(re.escape(o) for o in options) + r")",
                     re.I)
    tagged = tag.findall(text)
    if tagged:
        verdict = tagged[-1].upper()
    else:
        # No tag: take whichever option is mentioned first. CFG["aliases"] lets a known
        # option carry its inflections ("driving") without matching "driveway".
        best = None
        for opt in options:
            words = CFG.get("aliases", {}).get(opt.upper(), [opt])
            pat = re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.I)
            hit = pat.search(text)
            if hit and (best is None or hit.start() < best[0]):
                best = (hit.start(), opt)
        if not best:
            return False, "NONE"
        verdict = best[1].upper()
    return verdict == task["correct"].upper(), verdict


def run_contestant(entry, task):
    """Pass on the first attempt and stop; otherwise retry up to max_attempts."""
    started = time.time()
    prompt = build_prompt(task)
    total_tokens = total_thinking = 0
    total_in = total_out = total_cached = 0
    transcript = []
    passed = False

    for attempt in range(1, CFG["max_attempts"] + 1):
        try:
            caller = call_anthropic if entry["vendor"] == "anthropic" else call_openai
            res = caller(entry, prompt)
            ok, verdict = score(res["text"], task)
            total_tokens += res["tokens"]
            total_thinking += res["thinking"]
            total_in += res.get("tokens_in", 0)
            total_out += res.get("tokens_out", 0)
            total_cached += res.get("tokens_cached", 0)
            transcript.append({"attempt": attempt, "verdict": verdict,
                               "tokens": res["tokens"], "text": res["text"]})
        except Exception as exc:  # timeout, 429, anything - counts as a failed attempt
            ok = False
            transcript.append({"attempt": attempt, "verdict": "ERROR",
                               "tokens": 0, "text": str(exc)[:400]})
        if ok:
            passed = True
            break

    return {
        "id": entry["id"], "label": entry["label"], "badge": entry["badge"],
        "vendor": entry["vendor"], "passed": passed,
        "attempts": len(transcript), "tokens": total_tokens,
        "tokens_in": total_in, "tokens_out": total_out, "tokens_cached": total_cached,
        "cost_usd": cost_usd(entry, total_in, total_out, total_cached),
        "thinking": total_thinking, "seconds": round(time.time() - started, 1),
        "transcript": transcript,
    }


def run_all(emit, task):
    """Fan out all contestants at once; emit each result the moment it lands."""
    results = []
    with ThreadPoolExecutor(max_workers=len(CFG["roster"])) as pool:
        futures = {pool.submit(run_contestant, e, task): e for e in CFG["roster"]}
        for fut in as_completed(futures):
            entry = futures[fut]
            try:
                item = fut.result()
            except Exception as exc:
                item = {"id": entry["id"], "label": entry["label"],
                        "badge": entry["badge"], "vendor": entry["vendor"],
                        "passed": False, "attempts": 0, "tokens": 0,
                        "thinking": 0, "seconds": 0,
                        "transcript": [{"attempt": 0, "verdict": "ERROR",
                                        "tokens": 0, "text": str(exc)[:400]}]}
            results.append(item)
            emit("result", item)

    order = {e["id"]: i for i, e in enumerate(CFG["roster"])}
    results.sort(key=lambda r: order[r["id"]])
    payload = {"finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "task": task, "results": results}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = time.strftime("run-%Y%m%d-%H%M%S.json")
    with open(os.path.join(RESULTS_DIR, stamp), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    emit("done", payload)


def task_from_query(query):
    """Build the task from the UI's query string; fall back to the one in config.json.

    Scoring is a regex over a fixed option list, so a custom question has to be a
    two-way choice. Anything looser would need a judge model, which this demo
    deliberately does not have.
    """
    if not query:
        return dict(CFG["task"])

    params = parse_qs(query)
    question = params.get("q", [""])[0].strip()
    if not question:
        return dict(CFG["task"])

    options = [o.strip().upper() for o in params.get("options", [""])[0].split("|") if o.strip()]
    correct = params.get("correct", [""])[0].strip().upper()

    if len(options) != 2:
        raise ValueError("Give exactly two answer options.")
    if options[0] == options[1]:
        raise ValueError("The two answer options must be different.")
    if correct not in options:
        raise ValueError("The correct answer must be one of the two options.")

    return {"question": question, "options": options, "correct": correct,
            "why": params.get("why", [""])[0].strip()}



class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype):
        raw = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "index.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")

        elif path == "/config":
            self._send(200, json.dumps({"task": CFG["task"], "roster": CFG["roster"],
                                        "presets": CFG.get("presets", []),
                                        "pricing": CFG.get("pricing", {}),
                                        "commit": BUILD_COMMIT,
                                        "max_attempts": CFG["max_attempts"]}),
                       "application/json")

        elif path == "/health":
            # Readiness without spending anything: config parsed, roster present,
            # and a credential obtainable. Deliberately never calls a model, so it
            # can be polled before a demo without moving the cost needle.
            checks = {}
            try:
                checks["config"] = bool(CFG.get("roster")) and bool(CFG.get("endpoint"))
                checks["models_configured"] = len(CFG.get("roster", []))
                checks["pricing_configured"] = len(CFG.get("pricing", {}))
                checks["credential"] = bool(get_token())
                checks["credential_source"] = ("managed-identity"
                                               if os.environ.get("IDENTITY_ENDPOINT")
                                               else "azure-cli")
            except Exception as exc:
                checks["credential"] = False
                checks["error"] = str(exc)[:200]
            ready = bool(checks.get("config")) and bool(checks.get("credential"))
            payload = {"status": "ready" if ready else "degraded",
                       "commit": BUILD_COMMIT, "checks": checks}
            self._send(200 if ready else 503, json.dumps(payload), "application/json")

        elif path == "/run":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            def emit(event, data):
                chunk = "event: %s\ndata: %s\n\n" % (event, json.dumps(data))
                self.wfile.write(chunk.encode("utf-8"))
                self.wfile.flush()

            # Parsed after the headers so a bad question reports over SSE, where the
            # browser can actually read it, rather than as an opaque connection error.
            try:
                task = task_from_query(urlparse(self.path).query)
                emit("task", task)
                run_all(emit, task)
            except Exception as exc:
                try:
                    emit("fatal", {"error": str(exc)[:400]})
                except Exception:
                    pass
            self.close_connection = True

        else:
            self._send(404, "not found", "text/plain")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    # Containers and App Service must accept traffic from outside the loopback
    # interface; WEBSITE_SITE_NAME is set on App Service even without an identity.
    hosted = os.environ.get("IDENTITY_ENDPOINT") or os.environ.get("WEBSITE_SITE_NAME")
    host = "0.0.0.0" if hosted else "127.0.0.1"
    print("Checking Azure credentials...")
    get_token()
    print("Token OK. %d contestants ready." % len(CFG["roster"]))
    print("Listening on %s:%d" % (host, port))
    ThreadingHTTPServer((host, port), Handler).serve_forever()
