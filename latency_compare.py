# latency_compare.py
import time
import requests
import subprocess

BASE_URL = "http://127.0.0.1:8000/v1"
ITERATIONS = 50


def measure_response_times(label: str, iterations: int) -> dict:
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        response = requests.get(f"{BASE_URL}/books/?page=1&size=10")
        end = time.perf_counter()
        if response.status_code == 200:
            times.append((end - start) * 1000)  # convert to milliseconds

    return {
        "label":   label,
        "avg_ms":  sum(times) / len(times),
        "min_ms":  min(times),
        "max_ms":  max(times),
        "total_s": sum(times) / 1000,
        "count":   len(times)
    }


def print_result(result: dict):
    print(f"\n{'─' * 40}")
    print(f"  {result['label']}")
    print(f"{'─' * 40}")
    print(f"  Requests:  {result['count']}")
    print(f"  Avg:       {result['avg_ms']:.2f} ms")
    print(f"  Min:       {result['min_ms']:.2f} ms")
    print(f"  Max:       {result['max_ms']:.2f} ms")
    print(f"  Total:     {result['total_s']:.3f} s")


if __name__ == "__main__":
    print("\n📊 Day 21 — Before/After Cache Latency Comparison")
    print(f"   {ITERATIONS} requests per test\n")

    # ── WITHOUT CACHE ─────────────────────────────────────────────────
    # Flush Redis so every request hits Postgres
    subprocess.run(
        ["docker", "exec", "redis-book-api", "redis-cli", "FLUSHALL"],
        capture_output=True
    )
    print("🗑️  Redis flushed — cache is cold")

    # One warm-up request (TCP connection overhead)
    requests.get(f"{BASE_URL}/books/?page=1&size=10")

    # Flush again so warm-up doesn't prime the cache
    subprocess.run(
        ["docker", "exec", "redis-book-api", "redis-cli", "FLUSHALL"],
        capture_output=True
    )

    no_cache = measure_response_times("WITHOUT CACHE (Postgres every time)", ITERATIONS)
    print_result(no_cache)

    # ── WITH CACHE ────────────────────────────────────────────────────
    # First request primes the cache
    requests.get(f"{BASE_URL}/books/?page=1&size=10")
    print("\n✅ Cache primed — now measuring cache hits")

    with_cache = measure_response_times("WITH CACHE (Redis every time)", ITERATIONS)
    print_result(with_cache)

    # ── SUMMARY ───────────────────────────────────────────────────────
    speedup = no_cache["avg_ms"] / with_cache["avg_ms"]
    savings = no_cache["avg_ms"] - with_cache["avg_ms"]

    print(f"\n{'═' * 40}")
    print(f"  RESULT")
    print(f"{'═' * 40}")
    print(f"  Without cache: {no_cache['avg_ms']:.2f} ms avg")
    print(f"  With cache:    {with_cache['avg_ms']:.2f} ms avg")
    print(f"  Speedup:       {speedup:.1f}x faster")
    print(f"  Savings:       {savings:.2f} ms per request")
    print(f"{'═' * 40}\n")