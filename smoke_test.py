import urllib.request, json, time

t0 = time.time()
seen = 0
with urllib.request.urlopen("http://localhost:8000/run", timeout=400) as r:
    event = None
    for raw in r:
        line = raw.decode("utf-8", "replace").rstrip("\n")
        if line.startswith("event: "):
            event = line[7:]
        elif line.startswith("data: "):
            d = json.loads(line[6:])
            if event == "result":
                seen += 1
                v = [t["verdict"] for t in d["transcript"]]
                print(f"[{time.time()-t0:5.1f}s] {d['id']:<11} "
                      f"{'PASS' if d['passed'] else 'FAIL'} "
                      f"att={d['attempts']} tok={d['tokens']:<6} {v}")
                if not d["passed"] and d["transcript"]:
                    txt = d["transcript"][0]["text"][:160].replace("\n", " ")
                    print(f"              -> {txt}")
            elif event == "done":
                print(f"DONE in {time.time()-t0:.1f}s, {seen} results")
                break
            elif event == "fatal":
                print("FATAL:", d)
                break
