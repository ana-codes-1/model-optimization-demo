"""Run the full roster from the command line, no browser involved.

Starts the server itself if nothing is already listening, so `make test` works
from a clean clone. Exits non-zero if any model errored out, so it is usable as
a release gate — but a model answering *wrongly* is not a failure, since that is
the whole point of the demo.
"""
import json
import subprocess
import sys
import time
import urllib.request

# Model answers contain typographic quotes and dashes; the Windows console is
# cp1252 by default and turns them into mojibake.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 8000
BASE = "http://localhost:%d" % PORT


def server_is_up():
    try:
        urllib.request.urlopen(BASE + "/config", timeout=2).read()
        return True
    except Exception:
        return False


def start_server():
    proc = subprocess.Popen([sys.executable, "server.py"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    for _ in range(30):
        if proc.poll() is not None:
            sys.exit("server exited immediately:\n"
                     + proc.stderr.read().decode("utf-8", "replace"))
        if server_is_up():
            return proc
        time.sleep(0.5)
    proc.terminate()
    sys.exit("server did not come up on port %d within 15s" % PORT)


def main():
    started = None
    if server_is_up():
        print("using the server already running on port %d" % PORT)
    else:
        print("starting server on port %d" % PORT)
        started = start_server()

    t0 = time.time()
    seen = errors = 0
    try:
        with urllib.request.urlopen(BASE + "/run", timeout=400) as r:
            event = None
            for raw in r:
                line = raw.decode("utf-8", "replace").rstrip("\n")
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: "):
                    d = json.loads(line[6:])
                    if event == "result":
                        seen += 1
                        verdicts = [t["verdict"] for t in d["transcript"]]
                        if "ERROR" in verdicts:
                            errors += 1
                        print(f"[{time.time()-t0:5.1f}s] {d['id']:<11} "
                              f"{'PASS' if d['passed'] else 'FAIL'} "
                              f"att={d['attempts']} tok={d['tokens']:<6} "
                              f"${(d.get('cost_usd') or 0)*1000:6.2f}/1k {verdicts}")
                        if not d["passed"] and d["transcript"]:
                            txt = d["transcript"][0]["text"][:160].replace("\n", " ")
                            print(f"              -> {txt}")
                    elif event == "done":
                        passed = sum(1 for x in d["results"] if x["passed"])
                        total = sum(x.get("cost_usd") or 0 for x in d["results"])
                        print(f"DONE in {time.time()-t0:.1f}s - {passed}/{seen} correct, "
                              f"${total*1000:.2f} per 1k runs")
                        break
                    elif event == "fatal":
                        print("FATAL:", d)
                        return 1
    finally:
        if started:
            started.terminate()

    if not seen:
        print("no results streamed")
        return 1
    if errors:
        print(f"{errors} model(s) errored - that is a failure, unlike a wrong answer")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
