import sys
sys.path.insert(0, '.')

try:
    from app.database import Base, engine
    from app.models import models
    
    print("Importing models...")
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")
    
    # Test database connection
    from app.database import SessionLocal
    db = SessionLocal()
    print("✓ Database connection successful!")
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
