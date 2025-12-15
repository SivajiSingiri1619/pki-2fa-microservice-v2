import base64
import time
import pyotp


def _hex_to_base32(hex_seed: str) -> str:
    # hex -> bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # bytes -> base32 (string)
    return base64.b32encode(seed_bytes).decode("utf-8")


def generate_totp(hex_seed: str):
    base32_seed = _hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest="sha1"
    )

    code = totp.now()

    # remaining seconds in current window
    remaining = 30 - (int(time.time()) % 30)

    return code, remaining


def verify_totp(hex_seed: str, code: str) -> bool:
    base32_seed = _hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest="sha1"
    )

    # valid_window=1 → ±30 seconds
    return totp.verify(code, valid_window=1)
