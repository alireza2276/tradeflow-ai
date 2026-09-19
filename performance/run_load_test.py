#!/usr/bin/env python3
"""TradeFlowAI authenticated read-only load test.

Safety properties:
- GET-only workload after login: does not create/update/delete business data.
- Probes endpoints and only loads endpoints that return HTTP 200 for the supplied user.
- Stops escalating if error rate or latency becomes excessive.
- Uses only Python standard library.
"""
from __future__ import annotations

import argparse
import getpass
import json
import math
import os
import statistics
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener

DEFAULT_ENDPOINTS = [
    ("dashboard", "/api/trade/dashboard/"),
    ("companies", "/api/companies/?page=1"),
    ("registration_orders", "/api/trade/registration-orders/?page=1"),
    ("currency_purchases", "/api/trade/currency-purchases/?page=1"),
    ("shipment_parts", "/api/trade/shipment-parts/?page=1"),
    ("invoices", "/api/documents/invoices/?page=1"),
    ("notifications", "/api/notifications/logs/?page=1"),
    ("approval_requests", "/api/workflows/approval-requests/?page=1"),
    ("regulatory_deadlines", "/api/trade/regulatory-deadlines/?page=1"),
    ("customs_clearances", "/api/trade/customs-clearances/?page=1"),
]

@dataclass
class Result:
    name: str
    status: int
    elapsed_ms: float
    size: int
    error: str = ""


def percentile(values, p):
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def authenticate(base_url: str, username: str, password: str, timeout: float):
    jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    csrf_req = Request(base_url + "/api/auth/csrf/", method="GET")
    with opener.open(csrf_req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"CSRF endpoint returned HTTP {response.status}")

    csrf = None
    for cookie in jar:
        if cookie.name == "csrftoken":
            csrf = cookie.value
            break
    if not csrf:
        raise RuntimeError("csrftoken cookie was not returned by the server")

    payload = json.dumps({"username": username, "password": password}).encode("utf-8")
    req = Request(
        base_url + "/api/auth/login/",
        data=payload,
        headers={"Content-Type": "application/json", "X-CSRFToken": csrf},
        method="POST",
    )
    try:
        with opener.open(req, timeout=timeout) as response:
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"Login returned HTTP {response.status}: {body[:300]!r}")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Login failed: HTTP {exc.code}: {body[:500]}") from exc

    cookies = "; ".join(f"{c.name}={c.value}" for c in jar)
    if "sessionid=" not in cookies:
        raise RuntimeError("Login succeeded but no sessionid cookie was found")
    return cookies


def get_once(base_url, path, cookie_header, timeout, name):
    start = time.perf_counter()
    try:
        req = Request(
            base_url + path,
            headers={
                "Cookie": cookie_header,
                "Accept": "application/json",
                "Connection": "close",
                "User-Agent": "TradeFlowAI-LoadTest/1.0",
            },
            method="GET",
        )
        with build_opener().open(req, timeout=timeout) as response:
            body = response.read()
            return Result(name, response.status, (time.perf_counter() - start) * 1000, len(body))
    except HTTPError as exc:
        try:
            body = exc.read()
        except Exception:
            body = b""
        return Result(name, exc.code, (time.perf_counter() - start) * 1000, len(body), f"HTTP {exc.code}")
    except (URLError, TimeoutError, OSError) as exc:
        return Result(name, 0, (time.perf_counter() - start) * 1000, 0, type(exc).__name__)
    except Exception as exc:
        return Result(name, 0, (time.perf_counter() - start) * 1000, 0, type(exc).__name__)


def probe(base_url, cookie_header, timeout):
    print("\nProbing authenticated endpoints...")
    active = []
    for name, path in DEFAULT_ENDPOINTS:
        r = get_once(base_url, path, cookie_header, timeout, name)
        marker = "OK" if r.status == 200 else "SKIP"
        print(f"  {marker:4} {name:22} HTTP {r.status:<3} {r.elapsed_ms:8.1f} ms")
        if r.status == 200:
            active.append((name, path))
    return active


def run_stage(base_url, cookie_header, endpoints, concurrency, duration, timeout):
    results = []
    lock = threading.Lock()
    stop_at = time.monotonic() + duration
    start_gate = threading.Event()

    def worker(worker_id):
        local = []
        i = worker_id
        start_gate.wait()
        while time.monotonic() < stop_at:
            name, path = endpoints[i % len(endpoints)]
            local.append(get_once(base_url, path, cookie_header, timeout, name))
            i += 1
        with lock:
            results.extend(local)

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="tf-load") as pool:
        futures = [pool.submit(worker, i) for i in range(concurrency)]
        start_gate.set()
        for f in futures:
            f.result()
    elapsed = time.monotonic() - started
    return results, elapsed


def summarize(results, elapsed, concurrency):
    times = [r.elapsed_ms for r in results]
    ok = [r for r in results if 200 <= r.status < 300]
    errors = [r for r in results if not (200 <= r.status < 300)]
    total = len(results)
    return {
        "users": concurrency,
        "requests": total,
        "rps": total / elapsed if elapsed else 0,
        "avg_ms": statistics.fmean(times) if times else 0,
        "p50_ms": percentile(times, .50),
        "p95_ms": percentile(times, .95),
        "p99_ms": percentile(times, .99),
        "max_ms": max(times) if times else 0,
        "error_rate_pct": (len(errors) / total * 100) if total else 100,
        "status_counts": dict(Counter(r.status for r in results)),
        "successful": len(ok),
        "elapsed_s": elapsed,
    }


def endpoint_summary(results):
    grouped = defaultdict(list)
    for r in results:
        grouped[r.name].append(r)
    rows = []
    for name, rs in sorted(grouped.items()):
        times = [r.elapsed_ms for r in rs]
        bad = sum(not (200 <= r.status < 300) for r in rs)
        rows.append({
            "endpoint": name,
            "requests": len(rs),
            "avg_ms": statistics.fmean(times),
            "p95_ms": percentile(times, .95),
            "p99_ms": percentile(times, .99),
            "errors": bad,
        })
    return rows


def print_table(summaries):
    print("\nFINAL STAGE SUMMARY")
    print("users | requests |    RPS | avg ms | p95 ms | p99 ms | errors")
    print("------|----------|--------|--------|--------|--------|-------")
    for s in summaries:
        print(f"{s['users']:5} | {s['requests']:8} | {s['rps']:6.1f} | {s['avg_ms']:6.0f} | {s['p95_ms']:6.0f} | {s['p99_ms']:6.0f} | {s['error_rate_pct']:5.1f}%")


def main():
    parser = argparse.ArgumentParser(description="TradeFlowAI read-only authenticated load test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--stages", default="10,50,100,250,500,1000")
    parser.add_argument("--duration", type=int, default=15, help="seconds per stage")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--max-error-rate", type=float, default=20.0)
    parser.add_argument("--max-p95-ms", type=float, default=10000.0)
    parser.add_argument("--username", default=os.getenv("TF_LOAD_USERNAME", ""))
    parser.add_argument("--output", default="performance/load_test_report.json")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    username = args.username or input("TradeFlowAI username: ").strip()
    password = os.getenv("TF_LOAD_PASSWORD") or getpass.getpass("TradeFlowAI password: ")
    stages = [int(x.strip()) for x in args.stages.split(",") if x.strip()]

    print(f"\nTarget: {base_url}")
    print("Mode: authenticated GET-only workload (no business data mutations)")
    print("Authenticating once...")
    cookie_header = authenticate(base_url, username, password, args.timeout)
    print("Authentication: OK")

    endpoints = probe(base_url, cookie_header, args.timeout)
    if not endpoints:
        print("\nNo HTTP 200 endpoints available for this user. Aborting.")
        return 2
    print(f"\nActive endpoints: {len(endpoints)}")

    # Warm-up
    print("Warm-up: 5 users for 5 seconds...")
    run_stage(base_url, cookie_header, endpoints, 5, 5, args.timeout)

    summaries = []
    detailed = []
    for concurrency in stages:
        print(f"\n=== Stage: {concurrency} concurrent users, {args.duration}s ===")
        results, elapsed = run_stage(base_url, cookie_header, endpoints, concurrency, args.duration, args.timeout)
        s = summarize(results, elapsed, concurrency)
        ep = endpoint_summary(results)
        summaries.append(s)
        detailed.append({"users": concurrency, "endpoints": ep})
        print(f"Requests: {s['requests']} | RPS: {s['rps']:.1f} | Avg: {s['avg_ms']:.0f} ms | P95: {s['p95_ms']:.0f} ms | P99: {s['p99_ms']:.0f} ms | Errors: {s['error_rate_pct']:.1f}%")
        worst = sorted(ep, key=lambda x: x["p95_ms"], reverse=True)[:3]
        for row in worst:
            print(f"  {row['endpoint']:<22} p95={row['p95_ms']:.0f} ms  avg={row['avg_ms']:.0f} ms  errors={row['errors']}/{row['requests']}")

        if s["error_rate_pct"] > args.max_error_rate:
            print(f"Safety stop: error rate exceeded {args.max_error_rate:.1f}%.")
            break
        if s["p95_ms"] > args.max_p95_ms:
            print(f"Safety stop: P95 exceeded {args.max_p95_ms:.0f} ms.")
            break

        time.sleep(3)

    print_table(summaries)
    report = {
        "target": base_url,
        "mode": "authenticated-read-only",
        "duration_per_stage_s": args.duration,
        "endpoints": [{"name": n, "path": p} for n, p in endpoints],
        "stages": summaries,
        "endpoint_details": detailed,
        "note": "Results against Django runserver are diagnostic and are not production capacity numbers.",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nJSON report saved to: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
