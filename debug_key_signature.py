import hmac
import hashlib
import json
import base64

USER_KEY = "eyJleHBpcnkiOiIyMDI2LTAxLTE2IiwiY2xpZW50IjoiTWFuaXNoIiwiZmVhdHVyZXMiOlsiZW5hYmxlRXhwb3J0IiwiZW5hYmxlSW52b2ljZVByaW50aW5nIl0sImlzc3VlZF9hdCI6IjIwMjYtMDEtMTRUMTQ6NTg6NDcuNTMwMDU0In0=.28d73f503d1972362fdb14f45568b2e82e92a86aad7278de6c75156873c357c6"

SECRETS = {
    "DEFAULT": "default_insecure_key",
    "PRODUCTION": "super_secret_signing_key_2026"
}

def get_signature(secret, b64_payload):
    return hmac.new(
        secret.encode(),
        b64_payload.encode(),
        hashlib.sha256
    ).hexdigest()

parts = USER_KEY.split('.')
b64_payload = parts[0]
original_sig = parts[1]

print(f"Checking Key: {USER_KEY[:30]}...")
print(f"Original Sig: {original_sig}")

for name, secret in SECRETS.items():
    my_sig = get_signature(secret, b64_payload)
    match = hmac.compare_digest(original_sig, my_sig)
    print(f"Secret: {name} ({secret}) -> Sig: {my_sig} -> MATCH: {match}")
