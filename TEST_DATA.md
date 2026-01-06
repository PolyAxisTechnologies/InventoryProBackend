# Test Data Summary

## ✅ Database Successfully Seeded!

The database has been populated with comprehensive test data for hardware inventory management.

## 📊 Data Overview

### Categories (3)
1. **Nut-Bolts**
   - Description: Various sizes and qualities of nut-bolts
   - Qualities: 4 (GI, High Tension, Black, Stainless Steel)
   - Sizes: 6 (6mm to 16mm)
   - Items: 24 inventory items

2. **Springs (ISO-10243)**
   - Description: Compression springs as per ISO-10243 standard
   - Qualities: 5 (Green, Blue, Red, Yellow, Light Green)
   - Sizes: 5 (DIA 10 to DIA 25)
   - Items: 25 inventory items

3. **Ejector Pins (DIN 1530)**
   - Description: Ejector pins as per DIN 1530 standard
   - Qualities: 1 (Silver Steel Through Hardened)
   - Sizes: 6 (HT 1.0 to HT 4.0)
   - Items: 6 inventory items

### Total Inventory Items: **55**

### Suppliers (3)
1. **PIX Transmissions Limited**
   - Contact: Rajesh Kumar
   - Phone: 022-12345678
   - Location: Nagpur, Maharashtra

2. **Hardware Point Suppliers**
   - Contact: Amit Shah
   - Phone: 079-98765432
   - Location: Ahmedabad, Gujarat

3. **Indian Bank Hardware Division**
   - Contact: Priya Sharma
   - Phone: 080-11223344
   - Location: Bangalore, Karnataka

## 📦 Sample Items

### Nut-Bolts Examples:
- **NB-GI-6**: 6mm (1/4") GI Nut-Bolt - ₹5.00, Stock: 100 pcs
- **NB-HT-8**: 8mm (5/16") High Tension - ₹9.60, Stock: 110 pcs
- **NB-BL-10**: 10mm (3/8") Black - ₹5.60, Stock: 120 pcs
- **NB-ST-12**: 12mm (1/2") Stainless Steel - ₹22.50, Stock: 130 pcs

### Springs Examples:
- **SPR-GR-10**: DIA 10 Green Spring - ₹15.00, Stock: 80 pcs
- **SPR-BL-12**: DIA 12 Blue Spring - ₹24.00, Stock: 85 pcs
- **SPR-RE-16**: DIA 16 Red Spring - ₹45.00, Stock: 90 pcs
- **SPR-YE-20**: DIA 20 Yellow Spring - ₹81.00, Stock: 95 pcs

### Ejector Pins Examples:
- **PIN-SS-1.0**: HT 1.0 Silver Steel - ₹25.00, Stock: 60 pcs
- **PIN-SS-2.0**: HT 2.0 Silver Steel - ₹35.00, Stock: 68 pcs
- **PIN-SS-3.0**: HT 3.0 Silver Steel - ₹50.00, Stock: 76 pcs

## 🎯 Item Details

Each inventory item includes:
- **SKU**: Unique stock keeping unit code
- **Category, Quality, Size**: Full classification
- **Unit**: Measurement unit (pcs, kg, etc.)
- **Selling Price**: Price in rupees
- **GST**: 18% on all items
- **Stock Quantity**: Current stock level
- **Low Stock Threshold**: Alert threshold

## 🔄 Stock Levels

All items have been seeded with varying stock levels:
- Nut-Bolts: 100-230 pcs per item
- Springs: 80-200 pcs per item
- Ejector Pins: 60-100 pcs per item

Low stock thresholds set:
- Nut-Bolts: 50 pcs
- Springs: 30 pcs
- Ejector Pins: 25 pcs

## 🚀 How to Use

### View Data
```bash
python view_data.py
```

### Start API Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Access API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Test API Endpoints

**Get all categories:**
```
GET http://127.0.0.1:8000/api/categories
```

**Get qualities for Nut-Bolts (category_id=1):**
```
GET http://127.0.0.1:8000/api/qualities?category_id=1
```

**Get sizes for Springs (category_id=2):**
```
GET http://127.0.0.1:8000/api/sizes?category_id=2
```

## 🔄 Re-seed Database

To clear and re-add test data:
```bash
python seed_data.py
```

Type 'y' when prompted to confirm.

## 📝 Scripts Available

1. **seed_data.py** - Populate database with test data
2. **view_data.py** - View current database contents
3. **test_db.py** - Test database connection
4. **run.bat** - Start the API server

## ✅ Ready for Testing!

The backend is now fully populated with realistic test data and ready for:
- API endpoint testing
- Frontend development
- Integration testing
- Demo purposes

All data follows the structure from your paper-based system with proper categorization, qualities, and sizes!
