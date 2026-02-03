import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


DEFAULT_API_URL = "http://localhost:8000"
TESTS_PATH = Path("evaluation/regression_tests/questions.json")
REPORTS_DIR = Path("evaluation/reports")


def load_tests(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing tests file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def safe_lower(x: Optional[str]) -> str:
    return (x or "").lower()


def evaluate_one(
    api_url: str,
    test: Dict[str, Any],
    timeout_s: int = 120,
) -> Dict[str, Any]:
    question = test["question"]
    top_k = int(test.get("top_k", 2))
    expected_source_contains = test.get("expected_source_contains")
    expected_agent = test.get("expected_agent")

    payload = {"question": question, "top_k": top_k}

    start = time.perf_counter()
    resp = requests.post(f"{api_url}/ask", json=payload, timeout=timeout_s)
    latency_ms = int((time.perf_counter() - start) * 1000)

    ok_http = resp.status_code == 200
    data = resp.json() if ok_http else {"error": resp.text}

    agent = data.get("agent")
    answer = data.get("answer", "")
    sources = data.get("sources", []) or []

    # Checks
    has_sources = len(sources) > 0

    source_hit = None
    if expected_source_contains is None:
        # For "unknown" questions we expect NO strong KB source ideally
        # but we accept either no sources OR sources that don't look confident.
        source_hit = not has_sources
    else:
        source_hit = any(
            safe_lower(expected_source_contains) in safe_lower(s.get("file"))
            for s in sources
        )

    agent_match = (expected_agent is None) or (agent == expected_agent)

    return {
        "id": test.get("id"),
        "question": question,
        "expected_source_contains": expected_source_contains,
        "expected_agent": expected_agent,
        "http_status": resp.status_code,
        "latency_ms": latency_ms,
        "agent": agent,
        "answer_preview": (answer[:180] + "...") if len(answer) > 180 else answer,
        "sources": sources,
        "checks": {
            "ok_http": ok_http,
            "has_sources": has_sources,
            "source_hit": source_hit,
            "agent_match": agent_match,
        },
        "pass": bool(ok_http and source_hit and agent_match),
    }


def main():
    api_url = os.getenv("API_URL", DEFAULT_API_URL)

    tests = load_tests(TESTS_PATH)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    passed = 0

    print(f"Running {len(tests)} tests against {api_url} ...\n")

    for t in tests:
        r = evaluate_one(api_url, t)
        results.append(r)
        if r["pass"]:
            passed += 1

        status = "PASS" if r["pass"] else "FAIL"
        print(f"[{status}] {r['id']} | {r['latency_ms']}ms | agent={r['agent']}")
        if not r["pass"]:
            print("  checks:", r["checks"])
            if r.get("sources"):
                files = [s.get("file") for s in r["sources"]]
                print("  sources:", files)
            print()

    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "api_url": api_url,
        "total": len(tests),
        "passed": passed,
        "failed": len(tests) - passed,
        "pass_rate": round(passed / max(1, len(tests)), 3),
        "avg_latency_ms": int(sum(r["latency_ms"] for r in results) / max(1, len(results))),
    }

    report = {"summary": summary, "results": results}

    # Save timestamped report + latest.json
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    (REPORTS_DIR / f"report_{ts}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (REPORTS_DIR / "latest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nSummary:", summary)

    # Return non-zero exit on failure (useful for CI)
    if summary["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
