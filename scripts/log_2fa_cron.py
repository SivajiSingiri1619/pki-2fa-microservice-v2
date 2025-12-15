#!/usr/bin/env python3

import datetime
import base64
import pyotp
import os

SEED_PATH = "/data/seed.txt"
OUTPUT_PATH = "/cron/last_code.txt"


def hex_to_base32(hex_seed: str) -> str:
    return base64.b32encode(bytes.fromhex(hex_seed)).decode("utf-8")


def main():
    if not os.path.exists(SEED_PATH):
        print("Seed not found")
        return

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    base32_seed = hex_to_base32(hex_seed)

    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)

    code = totp.now()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{timestamp} - 2FA Code: {code}")


if __name__ == "__main__":
    main()
