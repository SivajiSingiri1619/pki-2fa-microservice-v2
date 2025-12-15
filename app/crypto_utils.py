import base64
import re
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def load_private_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    try:
        # 1. base64 decode
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)

        # 2. RSA OAEP SHA-256 decrypt
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        seed = decrypted.decode("utf-8").strip()

        # 3. validate seed (64 hex chars)
        if not re.fullmatch(r"[0-9a-f]{64}", seed):
            raise ValueError("Invalid seed format")

        return seed

    except Exception as e:
        raise RuntimeError("Decryption failed") from e
