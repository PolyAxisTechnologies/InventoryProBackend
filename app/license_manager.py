import os
import json
import base64
import hmac
import hashlib
from datetime import datetime
import threading

# Define App Data Path
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'InventoryPro')
os.makedirs(APP_DATA_DIR, exist_ok=True)

LICENSE_FILE = os.path.join(APP_DATA_DIR, "license.dat")
AUDIT_FILE = os.path.join(APP_DATA_DIR, "system_audit.dat")

class LicenseManager:
    def __init__(self):
        self._lock = threading.Lock()

    @property
    def secret_key(self):
        return os.getenv("LICENSE_SECRET_KEY", "default_insecure_key")

    def _get_signature(self, b64_payload: str) -> str:
        return hmac.new(
            self.secret_key.encode(),
            b64_payload.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_license_key(self, key: str):
        """
        Verifies signature and expiration of a license key.
        Returns: (bool: is_valid, dict: payload_or_error)
        """
        try:
            parts = key.split('.')
            if len(parts) != 2:
                return False, {"error": "Invalid key format"}
            
            b64_payload, signature = parts
            
            # 1. Verify Signature
            expected_sig = self._get_signature(b64_payload)
            if not hmac.compare_digest(signature, expected_sig):
                return False, {"error": "Invalid signature"}
            
            # 2. Decode Payload
            json_str = base64.urlsafe_b64decode(b64_payload).decode()
            payload = json.loads(json_str)
            
            # 3. Check Expiry
            expiry_str = payload.get("expiry")
            if not expiry_str:
                return False, {"error": "No expiry date in license"}
                
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if datetime.now().date() > expiry_date:
                return False, {"error": "License expired", "payload": payload}
                
            return True, payload
            
        except Exception as e:
            return False, {"error": str(e)}

    def save_license(self, key: str):
        """Saves a verified license to disk."""
        with self._lock:
            with open(LICENSE_FILE, "w") as f:
                f.write(key)

    def load_license(self):
        """Loads and verifies current license."""
        if not os.path.exists(LICENSE_FILE):
             # Default trial logic could go here, or return None
            return None
        
        with open(LICENSE_FILE, "r") as f:
            key = f.read().strip()
            
        is_valid, data = self.verify_license_key(key)
        if is_valid:
            return data
        return None

    def check_clock_tampering(self):
        """
        Anti-Rollback: Checks if system time is before the last recorded run time.
        Updates the last run time.
        """
        current_time = datetime.now().timestamp()
        
        last_time = 0.0
        if os.path.exists(AUDIT_FILE):
            try:
                with open(AUDIT_FILE, "r") as f:
                    content = f.read().strip()
                    if content:
                        last_time = float(content)
            except:
                pass # Corrupt file, maybe reset?
        
        # Allow small drift (e.g. 5 mins) or identical time, but not significant back travel
        # Actually identical time is fine.
        if current_time < last_time - 300: # 5 mins buffer
            return False, "System clock error detected. Please fix your date/time."
            
        # Update time
        try:
            with open(AUDIT_FILE, "w") as f:
                f.write(str(current_time))
        except:
             pass # Permission error?
             
        return True, "Clock OK"

license_manager = LicenseManager()
