"""Standalone diagnostic for the Go2 local-AP 'new method' handshake.

Run this while connected to the Go2's own WiFi hotspot (Toto):

    python diagnostics/diag_con_notify.py

It calls http://<robot_ip>:9991/con_notify directly and prints the raw
and decoded response so we can see why RSA public-key parsing fails,
without going through the full go2-webrtc-connect driver.
"""

import base64
import json
import sys

import requests

ROBOT_IP = "192.168.12.1"


def main() -> None:
    url = f"http://{ROBOT_IP}:9991/con_notify"
    print(f"POST {url}")
    try:
        resp = requests.post(url, data=None, headers=None, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    print(f"HTTP status: {resp.status_code}")
    raw = resp.text
    print(f"Raw response length: {len(raw)}")
    print(f"Raw response (first 300 chars): {raw[:300]!r}")

    try:
        decoded = base64.b64decode(raw).decode("utf-8")
    except Exception as e:
        print(f"base64 decode failed: {e!r}")
        sys.exit(1)

    print(f"\nDecoded (base64->utf8): {decoded}")

    try:
        parsed = json.loads(decoded)
    except Exception as e:
        print(f"JSON parse failed: {e!r}")
        sys.exit(1)

    print(f"\nParsed JSON keys: {list(parsed.keys())}")
    for k, v in parsed.items():
        if isinstance(v, str):
            print(f"  {k}: len={len(v)} value={v!r}")
        else:
            print(f"  {k}: {v!r}")

    data1 = parsed.get("data1", "")
    print(f"\ndata1 length: {len(data1)}")
    print(f"data1 first 20: {data1[:20]!r}")
    print(f"data1 last 20: {data1[-20:]!r}")

    pubkey_pem_candidate = data1[10 : len(data1) - 10]
    print(f"\nSliced candidate public key (data1[10:-10]), length {len(pubkey_pem_candidate)}:")
    print(pubkey_pem_candidate)

    try:
        key_bytes = base64.b64decode(pubkey_pem_candidate)
        print(f"\nDecoded key bytes length: {len(key_bytes)}")
        print(f"First 16 bytes hex: {key_bytes[:16].hex()}")
    except Exception as e:
        print(f"\nFailed to base64-decode sliced candidate: {e!r}")


if __name__ == "__main__":
    main()
