"""
Seed script to populate database with test data
Run this script to add sample categories, qualities, sizes, and items
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models.models import Category, Quality, Size, Item, Supplier
from datetime import datetime

def clear_database():
    """Clear all existing data"""
    print("Clearing existing data...")
    db = SessionLocal()
    try:
        db.query(Item).delete()
        db.query(Size).delete()
        db.query(Quality).delete()
        db.query(Category).delete()
        db.query(Supplier).delete()
        db.commit()
        print("✓ Database cleared")
    except Exception as e:
        print(f"✗ Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()


def seed_data():
    """Add test data to database"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("SEEDING DATABASE WITH TEST DATA")
        print("="*60 + "\n")
        
        # ==================== CATEGORY 1: NUT-BOLTS ====================
        print("📦 Creating Category: Nut-Bolts")
        cat_nutbolts = Category(
            name="Nut-Bolts",
            description="Various sizes and qualities of nut-bolts"
        )
        db.add(cat_nutbolts)
        db.commit()
        db.refresh(cat_nutbolts)
        print(f"   ✓ Category created (ID: {cat_nutbolts.id})")
        
        # Qualities for Nut-Bolts
        print("   Adding qualities...")
        qualities_nb = [
            Quality(category_id=cat_nutbolts.id, name="GI (Galvanized Iron)", description="Galvanized iron coating"),
            Quality(category_id=cat_nutbolts.id, name="High Tension", description="High tensile strength"),
            Quality(category_id=cat_nutbolts.id, name="Black", description="Black oxide finish"),
            Quality(category_id=cat_nutbolts.id, name="Stainless Steel", description="Corrosion resistant")
        ]
        db.add_all(qualities_nb)
        db.commit()
        for q in qualities_nb:
            db.refresh(q)
        print(f"   ✓ Added {len(qualities_nb)} qualities")
        
        # Sizes for Nut-Bolts
        print("   Adding sizes...")
        sizes_nb = [
            Size(category_id=cat_nutbolts.id, size_value="6", size_display='6mm (1/4")', sort_order=0),
            Size(category_id=cat_nutbolts.id, size_value="8", size_display='8mm (5/16")', sort_order=1),
            Size(category_id=cat_nutbolts.id, size_value="10", size_display='10mm (3/8")', sort_order=2),
            Size(category_id=cat_nutbolts.id, size_value="12", size_display='12mm (1/2")', sort_order=3),
            Size(category_id=cat_nutbolts.id, size_value="14", size_display='14mm (9/16")', sort_order=4),
            Size(category_id=cat_nutbolts.id, size_value="16", size_display='16mm (5/8")', sort_order=5),
        ]
        db.add_all(sizes_nb)
        db.commit()
        for s in sizes_nb:
            db.refresh(s)
        print(f"   ✓ Added {len(sizes_nb)} sizes")
        
        # Create Items (all combinations)
        print("   Creating inventory items...")
        items_created = 0
        base_prices = {"6": 5, "8": 6, "10": 7, "12": 9, "14": 11, "16": 13}
        quality_multipliers = {"GI (Galvanized Iron)": 1.0, "High Tension": 1.6, "Black": 0.8, "Stainless Steel": 2.5}
        
        for quality in qualities_nb:
            for size in sizes_nb:
                base_price = base_prices.get(size.size_value, 10)
                multiplier = quality_multipliers.get(quality.name, 1.0)
                price = round(base_price * multiplier, 2)
                
                item = Item(
                    category_id=cat_nutbolts.id,
                    quality_id=quality.id,
                    size_id=size.id,
                    sku=f"NB-{quality.name[:2].upper()}-{size.size_value}",
                    unit="pcs",
                    selling_price=price,
                    gst_percentage=18.0,
                    stock_quantity=100 + (items_created * 10),
                    low_stock_threshold=50
                )
                db.add(item)
                items_created += 1
        
        db.commit()
        print(f"   ✓ Created {items_created} inventory items")
        
        # ==================== CATEGORY 2: SPRINGS ====================
        print("\n📦 Creating Category: Springs (ISO-10243)")
        cat_springs = Category(
            name="Springs (ISO-10243)",
            description="Compression springs as per ISO-10243 standard"
        )
        db.add(cat_springs)
        db.commit()
        db.refresh(cat_springs)
        print(f"   ✓ Category created (ID: {cat_springs.id})")
        
        # Qualities for Springs (Colors)
        print("   Adding qualities (colors)...")
        qualities_springs = [
            Quality(category_id=cat_springs.id, name="Green", description="Light load"),
            Quality(category_id=cat_springs.id, name="Blue", description="Medium load"),
            Quality(category_id=cat_springs.id, name="Red", description="Heavy load"),
            Quality(category_id=cat_springs.id, name="Yellow", description="Extra heavy load"),
            Quality(category_id=cat_springs.id, name="Light Green", description="Very light load")
        ]
        db.add_all(qualities_springs)
        db.commit()
        for q in qualities_springs:
            db.refresh(q)
        print(f"   ✓ Added {len(qualities_springs)} qualities")
        
        # Sizes for Springs (Diameter)
        print("   Adding sizes...")
        sizes_springs = [
            Size(category_id=cat_springs.id, size_value="10", size_display="DIA 10", sort_order=0),
            Size(category_id=cat_springs.id, size_value="12", size_display="DIA 12", sort_order=1),
            Size(category_id=cat_springs.id, size_value="16", size_display="DIA 16", sort_order=2),
            Size(category_id=cat_springs.id, size_value="20", size_display="DIA 20", sort_order=3),
            Size(category_id=cat_springs.id, size_value="25", size_display="DIA 25", sort_order=4),
        ]
        db.add_all(sizes_springs)
        db.commit()
        for s in sizes_springs:
            db.refresh(s)
        print(f"   ✓ Added {len(sizes_springs)} sizes")
        
        # Create Spring Items
        print("   Creating inventory items...")
        items_created = 0
        spring_base_prices = {"10": 15, "12": 20, "16": 30, "20": 45, "25": 60}
        spring_color_multipliers = {"Green": 1.0, "Blue": 1.2, "Red": 1.5, "Yellow": 1.8, "Light Green": 0.9}
        
        for quality in qualities_springs:
            for size in sizes_springs:
                base_price = spring_base_prices.get(size.size_value, 20)
                multiplier = spring_color_multipliers.get(quality.name, 1.0)
                price = round(base_price * multiplier, 2)
                
                item = Item(
                    category_id=cat_springs.id,
                    quality_id=quality.id,
                    size_id=size.id,
                    sku=f"SPR-{quality.name[:2].upper()}-{size.size_value}",
                    unit="pcs",
                    selling_price=price,
                    gst_percentage=18.0,
                    stock_quantity=80 + (items_created * 5),
                    low_stock_threshold=30
                )
                db.add(item)
                items_created += 1
        
        db.commit()
        print(f"   ✓ Created {items_created} inventory items")
        
        # ==================== CATEGORY 3: EJECTOR PINS ====================
        print("\n📦 Creating Category: Ejector Pins")
        cat_pins = Category(
            name="Ejector Pins (DIN 1530)",
            description="Ejector pins as per DIN 1530 standard"
        )
        db.add(cat_pins)
        db.commit()
        db.refresh(cat_pins)
        print(f"   ✓ Category created (ID: {cat_pins.id})")
        
        # Qualities for Ejector Pins
        print("   Adding qualities...")
        qualities_pins = [
            Quality(category_id=cat_pins.id, name="Silver Steel Through Hardened", description="Hardness 52-58 HRC"),
        ]
        db.add_all(qualities_pins)
        db.commit()
        for q in qualities_pins:
            db.refresh(q)
        print(f"   ✓ Added {len(qualities_pins)} quality")
        
        # Sizes for Ejector Pins
        print("   Adding sizes...")
        sizes_pins = [
            Size(category_id=cat_pins.id, size_value="1.0", size_display="HT 1.0", sort_order=0),
            Size(category_id=cat_pins.id, size_value="1.5", size_display="HT 1.5", sort_order=1),
            Size(category_id=cat_pins.id, size_value="2.0", size_display="HT 2.0", sort_order=2),
            Size(category_id=cat_pins.id, size_value="2.5", size_display="HT 2.5", sort_order=3),
            Size(category_id=cat_pins.id, size_value="3.0", size_display="HT 3.0", sort_order=4),
            Size(category_id=cat_pins.id, size_value="4.0", size_display="HT 4.0", sort_order=5),
        ]
        db.add_all(sizes_pins)
        db.commit()
        for s in sizes_pins:
            db.refresh(s)
        print(f"   ✓ Added {len(sizes_pins)} sizes")
        
        # Create Ejector Pin Items
        print("   Creating inventory items...")
        items_created = 0
        pin_prices = {"1.0": 25, "1.5": 30, "2.0": 35, "2.5": 42, "3.0": 50, "4.0": 65}
        
        for quality in qualities_pins:
            for size in sizes_pins:
                price = pin_prices.get(size.size_value, 40)
                
                item = Item(
                    category_id=cat_pins.id,
                    quality_id=quality.id,
                    size_id=size.id,
                    sku=f"PIN-SS-{size.size_value}",
                    unit="pcs",
                    selling_price=price,
                    gst_percentage=18.0,
                    stock_quantity=60 + (items_created * 8),
                    low_stock_threshold=25
                )
                db.add(item)
                items_created += 1
        
        db.commit()
        print(f"   ✓ Created {items_created} inventory items")
        
        # ==================== SUPPLIERS ====================
        print("\n👥 Creating Suppliers...")
        suppliers = [
            Supplier(
                name="PIX Transmissions Limited",
                contact_person="Rajesh Kumar",
                phone="022-12345678",
                email="sales@pixtrans.com",
                address="Nagpur, Maharashtra"
            ),
            Supplier(
                name="Hardware Point Suppliers",
                contact_person="Amit Shah",
                phone="079-98765432",
                email="info@hardwarepoint.com",
                address="Ahmedabad, Gujarat"
            ),
            Supplier(
                name="Indian Bank Hardware Division",
                contact_person="Priya Sharma",
                phone="080-11223344",
                email="hardware@indianbank.com",
                address="Bangalore, Karnataka"
            )
        ]
        db.add_all(suppliers)
        db.commit()
        print(f"   ✓ Created {len(suppliers)} suppliers")
        
        # ==================== SUMMARY ====================
        print("\n" + "="*60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Count totals
        total_categories = db.query(Category).count()
        total_qualities = db.query(Quality).count()
        total_sizes = db.query(Size).count()
        total_items = db.query(Item).count()
        total_suppliers = db.query(Supplier).count()
        
        print(f"\n📊 Summary:")
        print(f"   Categories:  {total_categories}")
        print(f"   Qualities:   {total_qualities}")
        print(f"   Sizes:       {total_sizes}")
        print(f"   Items:       {total_items}")
        print(f"   Suppliers:   {total_suppliers}")
        
        print(f"\n✅ Test data ready for use!")
        print(f"   Start the server: uvicorn app.main:app --host 127.0.0.1 --port 8000")
        print(f"   View API docs: http://127.0.0.1:8000/docs")
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🌱 Database Seeding Script")
    print("="*60)
    
    response = input("\nThis will clear existing data and add test data. Continue? (y/n): ")
    
    if response.lower() == 'y':
        clear_database()
        seed_data()
    else:
        print("Cancelled.")
