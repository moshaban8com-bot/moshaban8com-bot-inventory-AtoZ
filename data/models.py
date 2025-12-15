"""
Database models for the Inventory Management System
نماذج قاعدة البيانات
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Boolean, Numeric,
    ForeignKey, Text, Enum, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum

from data.database import Base


# Enums
class DocumentStatus(enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    APPROVED = 'APPROVED'
    POSTED = 'POSTED'
    CANCELLED = 'CANCELLED'
    REVERSED = 'REVERSED'


class DocumentType(enum.Enum):
    GRN_RECEIPT = 'GRN_RECEIPT'
    RETURN_IN = 'RETURN_IN'
    ISSUE = 'ISSUE'
    RETURN_OUT = 'RETURN_OUT'
    TRANSFER = 'TRANSFER'
    ADJUSTMENT = 'ADJUSTMENT'
    STOCK_COUNT = 'STOCK_COUNT'
    PRODUCTION_ORDER = 'PRODUCTION_ORDER'
    PRODUCTION_ISSUE = 'PRODUCTION_ISSUE'
    PRODUCTION_RECEIPT = 'PRODUCTION_RECEIPT'
    SCRAP = 'SCRAP'


class ItemType(enum.Enum):
    STOCK = 'STOCK'
    NON_STOCK = 'NON_STOCK'
    SERVICE = 'SERVICE'


class TrackingType(enum.Enum):
    NONE = 'NONE'
    LOT = 'LOT'
    SERIAL = 'SERIAL'
    LOT_EXPIRY = 'LOT_EXPIRY'


class PolicyScope(enum.Enum):
    GLOBAL = 'GLOBAL'
    COMPANY = 'COMPANY'
    WAREHOUSE = 'WAREHOUSE'
    DOCTYPE = 'DOCTYPE'
    CATEGORY = 'CATEGORY'
    ITEM = 'ITEM'


# ============= Core Tables =============

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    currency = Column(String(3), nullable=False, default='EGP')  # ISO 4217
    fiscal_year_start = Column(Date, nullable=False)
    fiscal_year_end = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    warehouses = relationship('Warehouse', back_populates='company')
    modules = relationship('CompanyModule', back_populates='company')
    
    def __repr__(self):
        return f"<Company(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class CompanyModule(Base):
    __tablename__ = 'company_modules'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    module_name = Column(String(50), nullable=False)  # INVENTORY, MANUFACTURING, SALES, PURCHASING, QC
    is_enabled = Column(Boolean, default=True)
    enabled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', back_populates='modules')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'module_name', name='uq_company_module'),
    )
    
    def __repr__(self):
        return f"<CompanyModule(company_id={self.company_id}, module='{self.module_name}', enabled={self.is_enabled})>"


class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    is_in_transit = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', back_populates='warehouses')
    locations = relationship('Location', back_populates='warehouse')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_warehouse_code'),
    )
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    code = Column(String(50), nullable=False)
    zone = Column(String(50))
    rack = Column(String(50))
    shelf = Column(String(50))
    bin = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    warehouse = relationship('Warehouse', back_populates='locations')
    
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'code', name='uq_location_code'),
    )
    
    def __repr__(self):
        return f"<Location(id={self.id}, code='{self.code}', warehouse_id={self.warehouse_id})>"


# ============= Item Master Data =============

class ItemCategory(Base):
    __tablename__ = 'item_categories'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey('item_categories.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship('Item', back_populates='category')
    parent = relationship('ItemCategory', remote_side=[id])
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_category_code'),
    )
    
    def __repr__(self):
        return f"<ItemCategory(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class UOM(Base):
    __tablename__ = 'uoms'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<UOM(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(50), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    description_ar = Column(Text)
    description_en = Column(Text)
    category_id = Column(Integer, ForeignKey('item_categories.id'))
    brand = Column(String(100))
    item_type = Column(Enum(ItemType), default=ItemType.STOCK)
    tracking_type = Column(Enum(TrackingType), default=TrackingType.NONE)
    base_uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    
    # Inventory control
    min_qty = Column(Numeric(18, 4), default=0)
    max_qty = Column(Numeric(18, 4), default=0)
    reorder_point = Column(Numeric(18, 4), default=0)
    safety_stock = Column(Numeric(18, 4), default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship('ItemCategory', back_populates='items')
    base_uom = relationship('UOM')
    uom_conversions = relationship('ItemUOMConversion', back_populates='item')
    barcodes = relationship('Barcode', back_populates='item')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_item_code'),
    )
    
    def __repr__(self):
        return f"<Item(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class ItemUOMConversion(Base):
    __tablename__ = 'item_uom_conversions'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    from_uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    to_uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    conversion_factor = Column(Numeric(18, 6), nullable=False)
    
    # Relationships
    item = relationship('Item', back_populates='uom_conversions')
    from_uom = relationship('UOM', foreign_keys=[from_uom_id])
    to_uom = relationship('UOM', foreign_keys=[to_uom_id])
    
    __table_args__ = (
        UniqueConstraint('item_id', 'from_uom_id', 'to_uom_id', name='uq_item_uom_conversion'),
    )
    
    def __repr__(self):
        return f"<ItemUOMConversion(item_id={self.item_id}, factor={self.conversion_factor})>"


class Barcode(Base):
    __tablename__ = 'barcodes'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    barcode = Column(String(100), unique=True, nullable=False)
    uom_id = Column(Integer, ForeignKey('uoms.id'))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship('Item', back_populates='barcodes')
    uom = relationship('UOM')
    
    def __repr__(self):
        return f"<Barcode(id={self.id}, barcode='{self.barcode}', item_id={self.item_id})>"


# ============= Parties =============

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_supplier_code'),
    )
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_customer_code'),
    )
    
    def __repr__(self):
        return f"<Customer(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class ReasonCode(Base):
    __tablename__ = 'reason_codes'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    reason_type = Column(String(50), nullable=False)  # ADJUSTMENT, SCRAP, OVERRIDE
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_reason_code'),
    )
    
    def __repr__(self):
        return f"<ReasonCode(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


# ============= Tracking =============

class Lot(Base):
    __tablename__ = 'lots'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    lot_number = Column(String(100), nullable=False)
    manufacture_date = Column(Date)
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship('Item')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'item_id', 'lot_number', name='uq_lot'),
    )
    
    def __repr__(self):
        return f"<Lot(id={self.id}, lot_number='{self.lot_number}', item_id={self.item_id})>"


class Serial(Base):
    __tablename__ = 'serials'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    serial_number = Column(String(100), nullable=False)
    lot_id = Column(Integer, ForeignKey('lots.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship('Item')
    lot = relationship('Lot')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'item_id', 'serial_number', name='uq_serial'),
    )
    
    def __repr__(self):
        return f"<Serial(id={self.id}, serial_number='{self.serial_number}', item_id={self.item_id})>"


# Make all models available for import
__all__ = [
    'Base',
    'DocumentStatus', 'DocumentType', 'ItemType', 'TrackingType', 'PolicyScope',
    'Company', 'CompanyModule', 'Warehouse', 'Location',
    'ItemCategory', 'UOM', 'Item', 'ItemUOMConversion', 'Barcode',
    'Supplier', 'Customer', 'ReasonCode',
    'Lot', 'Serial',
]
