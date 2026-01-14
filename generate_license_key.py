import hmac
import hashlib
import json
import base64
import os
from datetime import datetime

# NOTE: The V2 App is falling back to the default key in some environments.
# To ensure the key works for you NOW, we match that default.
SECRET_KEY = "default_insecure_key"

def generate_key(client_name, expiry_date, features=None):
    if features is None:
        features = ["enableExport", "enableInvoicePrinting"]
        
    payload = {
        "expiry": expiry_date, # YYYY-MM-DD
        "client": client_name,
        "features": features,
        "issued_at": datetime.now().isoformat()
    }
    
    # 1. Create JSON Payload
    json_str = json.dumps(payload, separators=(',', ':'))
    
    # 2. Base64 Encode
    b64_payload = base64.urlsafe_b64encode(json_str.encode()).decode()
    
    # 3. Sign it
    signature = hmac.new(
        SECRET_KEY.encode(),
        b64_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 4. Combine
    final_key = f"{b64_payload}.{signature}"
    return final_key

if __name__ == "__main__":
    print("\n=== LICENSE KEY GENERATOR ===")
    
    # Get interactive input
    client_name = input("Enter Client Name: ").strip()
    if not client_name:
        print("Error: Client Name is required.")
        exit(1)
        
    date_input = input("Enter Expiry Date (YYYY-MM-DD) [Default: 2026-01-01]: ").strip()
    if not date_input:
        expiry_date = "2026-01-01"
    else:
        expiry_date = date_input

    # Features Input
    features = []
    
    if input("Enable 'Export to Excel'? (y/N): ").lower().startswith('y'):
        features.append("enableExport")
        
    if input("Enable 'Invoice Printing'? (y/N): ").lower().startswith('y'):
        features.append("enableInvoicePrinting")

    # Generate
    key = generate_key(client_name, expiry_date, features)
    
    print("\n" + "="*60)
    print(f"GENERATED KEY FOR: {client_name}")
    print(f"Expires: {expiry_date}")
    print(f"Features: {', '.join(features) if features else 'None'}")
    print("="*60)
    print(key)
    print("="*60 + "\n")
    
    # Save to file conveniently
    with open("key.txt", "w") as f:
        f.write(key)
    print("(Key also saved to key.txt)")
