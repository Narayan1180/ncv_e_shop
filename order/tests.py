from django.test import TestCase

# Create your tests here.
"""
Simple script: use an ALREADY-ISSUED JWT access token (e.g. copied from
your browser's dev tools -> Application -> Cookies), set it directly as
a cookie, then call checkout 1000 times in a loop and print a summary.

No login call needed — you're supplying the token yourself.

USAGE:
    pip install requests
    python hit_checkout.py
"""

import requests
import uuid
import time
    
"""
Fires many checkout requests CONCURRENTLY (simulating N real users hitting
the endpoint at the same moment), instead of one-by-one sequentially.

This is what actually stresses select_for_update() locking, DB connection
pooling, and reveals race conditions — a sequential loop cannot surface
any of that, since nothing is ever competing for the same resources.

USAGE:
    pip install requests
    python hit_checkout_concurrent.py
"""

import requests
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"
CHECKOUT_URL = f"{BASE_URL}/orders/checkout"

COOKIE_NAME = "access_token"
ACCESS_TOKEN = "PASTE_YOUR_TOKEN_HERE"

PRODUCT_ID = 1
TOTAL_REQUESTS = 1000
CONCURRENT_WORKERS = 100   # <-- this is your "how many users AT ONCE" knob

BASE_URL = "http://localhost:8000"
CHECKOUT_URL = f"{BASE_URL}/orders/checkout/"

# Paste your existing access token here (copy the VALUE only, not the
# whole "cookiename=value" string, from your browser's dev tools).
COOKIE_NAME = "access_token"   # must match whatever your JWTCookieAuthentication reads
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzkwNDc2NDI1LCJpYXQiOjE3OTA0NjU2MjUsImp0aSI6IjZjN2U0YTVhMjdkODRjY2RiNGVmMTU2YjViNWRjMWViIiwidXNlcl9pZCI6IjMifQ.uyB5HFfiec94ngANwVijomsAL0EFmCSLzrGCLcIGGfk"
PRODUCT_ID = 1                       # adjust to a real product with stock
NUM_REQUESTS = 1000
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Idempotency-Key": str(uuid.uuid4()),
     }


def make_request(_):
    """Each call creates its own session — real users don't share a
    connection, and reusing one requests.Session across threads can
    behave oddly under heavy concurrency."""
    session = requests.Session()
    session.cookies.set(COOKIE_NAME, ACCESS_TOKEN, domain="localhost")

    idempotency_key = str(uuid.uuid4())
    start = time.time()
    try:
        resp = session.post(
            CHECKOUT_URL,
            json={"product_id": PRODUCT_ID, "quantity": 1},
            headers=headers,
            timeout=30,
        )
        elapsed = time.time() - start
        return resp.status_code, elapsed
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start
        return f"ERROR: {e}", elapsed


def main():
    results = {}
    durations = []

    start_all = time.time()

    # This is the key difference from your sequential loop: all these
    # requests are dispatched to run AT THE SAME TIME across
    # CONCURRENT_WORKERS threads, instead of waiting for each to finish
    # before starting the next.
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(make_request, i) for i in range(TOTAL_REQUESTS)]

        completed = 0
        for future in as_completed(futures):
            status, elapsed = future.result()
            results[status] = results.get(status, 0) + 1
            durations.append(elapsed)
            completed += 1
            if completed % 100 == 0:
                print(f"{completed}/{TOTAL_REQUESTS} completed...")

    total_time = time.time() - start_all

    print("\n--- Summary (CONCURRENT) ---")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Concurrent workers: {CONCURRENT_WORKERS}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests/sec: {TOTAL_REQUESTS / total_time:.2f}")
    print(f"Avg response time: {sum(durations) / len(durations) * 1000:.1f}ms")
    print(f"Max response time: {max(durations) * 1000:.1f}ms")
    print("\nStatus code breakdown:")
    for code, count in sorted(results.items(), key=lambda x: str(x[0])):
        print(f"  {code}: {count}")


if __name__ == "__main__":
    main()