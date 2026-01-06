# Mahendra Hardware Inventory - Backend

Python FastAPI backend for the hardware inventory management system.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   # Using the batch script (Windows)
   run.bat
   
   # Or manually
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   
   # With auto-reload for development
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Project Structure

```
InventoryProBackend/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── routers/         # API route handlers
│   ├── utils/           # Utility functions (logging, audit)
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── logs/                # Daily log files
├── venv/                # Virtual environment
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── inventory.db         # SQLite database
└── run.bat              # Quick start script
```

## API Endpoints

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create category
- `GET /api/categories/{id}` - Get category details
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Qualities
- `GET /api/qualities?category_id={id}` - List qualities (filtered by category)
- `POST /api/qualities` - Create quality
- `GET /api/qualities/{id}` - Get quality details
- `PUT /api/qualities/{id}` - Update quality
- `DELETE /api/qualities/{id}` - Delete quality

### Sizes
- `GET /api/sizes?category_id={id}` - List sizes (filtered by category)
- `POST /api/sizes` - Create size
- `POST /api/sizes/bulk` - Create multiple sizes from range
- `GET /api/sizes/{id}` - Get size details
- `PUT /api/sizes/{id}` - Update size
- `DELETE /api/sizes/{id}` - Delete size

## Database

- **Type**: SQLite
- **File**: `inventory.db`
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic (to be set up)

### Tables
- `categories` - Product categories
- `qualities` - Product qualities/variants
- `sizes` - Product sizes
- `items` - Inventory items
- `suppliers` - Supplier information
- `purchases` - Purchase records
- `purchase_items` - Purchase line items
- `sales` - Sales records
- `sale_items` - Sale line items
- `audit_logs` - Audit trail for all operations

## Logging

- **Daily log files**: `logs/YYYY-MM-DD.log`
- **Retention**: 60 days
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Audit logs**: All INSERT, UPDATE, DELETE operations logged to database

## Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=sqlite:///./inventory.db
API_HOST=127.0.0.1
API_PORT=8000
```

## Development

- **Auto-reload**: Use `--reload` flag with uvicorn
- **Debug logs**: Check `logs/` directory
- **API testing**: Use Swagger UI at `/docs`

## Future Migration to Supabase

The database is designed for easy migration to PostgreSQL/Supabase:
- Using SQLAlchemy ORM (database-agnostic)
- Standard data types (no SQLite-specific features)
- Timezone-aware timestamps
- Proper foreign key constraints
- JSON support for flexible data

To migrate:
1. Export data from SQLite
2. Update `DATABASE_URL` in `.env` to PostgreSQL connection string
3. Run Alembic migrations
4. Import data
