from app.totp_utils import generate_totp, verify_totp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from app.crypto_utils import load_private_key, decrypt_seed

DATA_DIR = "/data"
SEED_PATH = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_PATH = "student_private.pem"

app = FastAPI(title="PKI + TOTP Microservice")


class DecryptRequest(BaseModel):
    encrypted_seed: str
class VerifyRequest(BaseModel):
    code: str

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: DecryptRequest):
    try:
        # load private key
        private_key = load_private_key(PRIVATE_KEY_PATH)

        # decrypt seed
        seed = decrypt_seed(req.encrypted_seed, private_key)

        # ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)

        # save seed persistently
        with open(SEED_PATH, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        with open(SEED_PATH, "r") as f:
            seed = f.read().strip()

        code, valid_for = generate_totp(seed)

        return {
            "code": code,
            "valid_for": valid_for
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate 2FA")
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        with open(SEED_PATH, "r") as f:
            seed = f.read().strip()

        is_valid = verify_totp(seed, req.code)

        return {
            "valid": is_valid
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Verification failed")
