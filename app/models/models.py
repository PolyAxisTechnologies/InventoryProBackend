from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    qualities = relationship("Quality", back_populates="category", cascade="all, delete-orphan")
    sizes = relationship("Size", back_populates="category", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")


class Quality(Base):
    __tablename__ = "qualities"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="qualities")
    items = relationship("Item", back_populates="quality", cascade="all, delete-orphan")


class Size(Base):
    __tablename__ = "sizes"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    size_value = Column(String(50), nullable=False)  # e.g., "6", "8", "10"
    size_display = Column(String(100), nullable=False)  # e.g., "6mm (1/4\")", "8mm (5/16\")"
    sort_order = Column(Integer, default=0)  # For custom ordering
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="sizes")
    items = relationship("Item", back_populates="size", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    quality_id = Column(Integer, ForeignKey("qualities.id", ondelete="CASCADE"), nullable=False, index=True)
    size_id = Column(Integer, ForeignKey("sizes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sku = Column(String(100), unique=True, nullable=True)  # Stock Keeping Unit
    unit = Column(String(50), nullable=False, default="pcs")  # pcs, kg, meter, dozen, etc.
    selling_price = Column(Float, nullable=False, default=0.0)
    gst_percentage = Column(Float, nullable=False, default=0.0)  # 0, 5, 9, 18
    stock_quantity = Column(Float, nullable=False, default=0.0, index=True)
    low_stock_threshold = Column(Float, nullable=False, default=10.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="items")
    quality = relationship("Quality", back_populates="items")
    size = relationship("Size", back_populates="items")
    sale_items = relationship("SaleItem", back_populates="item")
    purchase_items = relationship("PurchaseItem", back_populates="item")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    purchases = relationship("Purchase", back_populates="supplier")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    purchase_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="purchases")
    purchase_items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    purchase = relationship("Purchase", back_populates="purchase_items")
    item = relationship("Item", back_populates="purchase_items")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    gst_amount = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    gst_percentage = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sale = relationship("Sale", back_populates="sale_items")
    item = relationship("Item", back_populates="sale_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False, index=True)  # INSERT, UPDATE, DELETE
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    user_id = Column(Integer, nullable=True)  # For future multi-user support
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String(200), nullable=False, default="Hardware Point")
    shop_address = Column(Text, nullable=True)
    shop_phone = Column(String(20), nullable=True)
    shop_email = Column(String(100), nullable=True)
    shop_gstin = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

