"""
DataMorph Studio - Security, Authentication & Cryptography
Implements secure password hashing (PBKDF2-HMAC-SHA256), token generation,
and session management without external dependencies.
"""

import hashlib
import hmac
import secrets
import time
import base64
import json
from typing import Dict, Optional, Tuple

SECRET_KEY = b"datamorph-enterprise-ml-secret-key-2026-production"
SALT_BYTES = 16
HASH_ITERATIONS = 100000


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = secrets.token_bytes(SALT_BYTES)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    encoded_salt = base64.b64encode(salt).decode("utf-8")
    encoded_key = base64.b64encode(key).decode("utf-8")
    return f"pbkdf2:sha256:{HASH_ITERATIONS}${encoded_salt}${encoded_key}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored PBKDF2 hash."""
    try:
        header, encoded_salt, encoded_key = hashed_password.split("$")
        parts = header.split(":")
        iterations = int(parts[2])
        salt = base64.b64decode(encoded_salt.encode("utf-8"))
        expected_key = base64.b64decode(encoded_key.encode("utf-8"))
        derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(expected_key, derived_key)
    except Exception:
        return False


def generate_token(user_id: str, username: str, role: str = "engineer", expires_in_sec: int = 86400) -> str:
    """Generates a signed, self-contained authentication token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": int(time.time()) + expires_in_sec,
        "nonce": secrets.token_hex(8)
    }
    payload_json = json.dumps(payload).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    signature = hmac.new(SECRET_KEY, payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    return f"{payload_b64}.{sig_b64}"


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies and decodes a signed authentication token."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig_b64 = parts
        expected_sig = hmac.new(SECRET_KEY, payload_b64.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)).decode("utf-8")
        payload = json.loads(payload_json)
        if time.time() > payload.get("exp", 0):
            return None
        return payload
    except Exception:
        return None
