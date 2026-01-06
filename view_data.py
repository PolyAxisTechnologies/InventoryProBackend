"""
Quick script to view database contents
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.models import Category, Quality, Size, Item, Supplier

def view_data():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("DATABASE CONTENTS")
        print("="*70 + "\n")
        
        # Categories
        categories = db.query(Category).all()
        print(f"📦 CATEGORIES ({len(categories)}):")
        for cat in categories:
            print(f"   [{cat.id}] {cat.name}")
            
            # Qualities for this category
            qualities = db.query(Quality).filter(Quality.category_id == cat.id).all()
            print(f"       Qualities: {', '.join([q.name for q in qualities])}")
            
            # Sizes for this category
            sizes = db.query(Size).filter(Size.category_id == cat.id).order_by(Size.sort_order).all()
            print(f"       Sizes: {', '.join([s.size_display for s in sizes])}")
            
            # Item count
            item_count = db.query(Item).filter(Item.category_id == cat.id).count()
            print(f"       Items: {item_count} inventory items")
            print()
        
        # Suppliers
        suppliers = db.query(Supplier).all()
        print(f"\n👥 SUPPLIERS ({len(suppliers)}):")
        for sup in suppliers:
            print(f"   [{sup.id}] {sup.name} - {sup.contact_person} ({sup.phone})")
        
        # Sample Items
        print(f"\n📊 SAMPLE ITEMS (first 10):")
        items = db.query(Item).limit(10).all()
        for item in items:
            category = db.query(Category).filter(Category.id == item.category_id).first()
            quality = db.query(Quality).filter(Quality.id == item.quality_id).first()
            size = db.query(Size).filter(Size.id == item.size_id).first()
            
            print(f"   [{item.id}] {item.sku}")
            print(f"       {category.name} > {quality.name} > {size.size_display}")
            print(f"       Price: ₹{item.selling_price} | Stock: {item.stock_quantity} {item.unit} | GST: {item.gst_percentage}%")
        
        # Totals
        total_items = db.query(Item).count()
        total_stock_value = sum([item.selling_price * item.stock_quantity for item in db.query(Item).all()])
        
        print(f"\n" + "="*70)
        print(f"SUMMARY:")
        print(f"   Total Items: {total_items}")
        print(f"   Total Stock Value: ₹{total_stock_value:,.2f}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    view_data()
