import uvicorn
import os
import sys
import sqlalchemy
import pydantic
from app.main import app

if __name__ == "__main__":
    # Freeze support for multiprocessing if used
    import multiprocessing
    multiprocessing.freeze_support() 
    
    # Ensure environment variables are loaded if we bundle .env or expect it
    # But for a bundled app, we might want defaults or write a fresh .env
    # For now, we rely on the app loading .env if present or using defaults.
    
    # IMPORTANT: When running frozen, we might need to adjust paths
    if getattr(sys, 'frozen', False):
         os.chdir(os.path.dirname(sys.executable))
         # Inject Production Secrets for Deployed App
         os.environ["LICENSE_SECRET_KEY"] = "super_secret_signing_key_2026"
         os.environ["VITE_ADMIN_SAVE_PASSWORD"] = "securepass123"

    # CRITICAL: Do NOT use workers=1 when frozen with app object. It triggers reload/import logic.
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
