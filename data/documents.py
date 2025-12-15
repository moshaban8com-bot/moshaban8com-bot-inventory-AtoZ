"""
Document and Ledger models
نماذج المستندات ودفتر الحركة
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Boolean, Numeric,
    ForeignKey, Text, Enum, Index
)
from sqlalchemy.orm import relationship

from data.database import Base
from data.models import DocumentStatus, DocumentType


class DocumentSequence(Base):
    __tablename__ = 'doc_sequences'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    doc_type = Column(Enum(DocumentType), nullable=False)
    prefix = Column(String(20), nullable=False)
    next_number = Column(Integer, default=1)
    padding = Column(Integer, default=6)  # Number of digits
    
    def get_next_doc_no(self):
        """Generate next document number"""
        doc_no = f"{self.prefix}{str(self.next_number).zfill(self.padding)}"
        self.next_number += 1
        return doc_no
    
    def __repr__(self):
        return f"<DocumentSequence(company_id={self.company_id}, doc_type='{self.doc_type}', prefix='{self.prefix}')>"


class DocumentHeader(Base):
    __tablename__ = 'documents_header'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    doc_type = Column(Enum(DocumentType), nullable=False)
    doc_no = Column(String(50), nullable=False)
    doc_date = Column(Date, nullable=False)
    
    # Status and workflow
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    posting_date = Column(Date)
    
    # Warehouses
    from_warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    to_warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    
    # Party references
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Reference
    reference_no = Column(String(100))
    notes = Column(Text)
    
    # Reason
    reason_code_id = Column(Integer, ForeignKey('reason_codes.id'))
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_by = Column(Integer, ForeignKey('users.id'))
    submitted_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    posted_by = Column(Integer, ForeignKey('users.id'))
    posted_at = Column(DateTime)
    
    # Relationships
    from_warehouse = relationship('Warehouse', foreign_keys=[from_warehouse_id])
    to_warehouse = relationship('Warehouse', foreign_keys=[to_warehouse_id])
    supplier = relationship('Supplier')
    customer = relationship('Customer')
    reason_code = relationship('ReasonCode')
    lines = relationship('DocumentLine', back_populates='header', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_doc_company_type_no', 'company_id', 'doc_type', 'doc_no'),
        Index('idx_doc_status', 'status'),
        Index('idx_doc_posting_date', 'posting_date'),
    )
    
    def __repr__(self):
        return f"<DocumentHeader(id={self.id}, doc_type='{self.doc_type}', doc_no='{self.doc_no}', status='{self.status}')>"


class DocumentLine(Base):
    __tablename__ = 'documents_lines'
    
    id = Column(Integer, primary_key=True)
    header_id = Column(Integer, ForeignKey('documents_header.id'), nullable=False)
    line_no = Column(Integer, nullable=False)
    
    # Item
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    
    # Quantity and UOM
    qty = Column(Numeric(18, 4), nullable=False)
    uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    base_qty = Column(Numeric(18, 4), nullable=False)  # Quantity in base UOM
    
    # Locations
    from_location_id = Column(Integer, ForeignKey('locations.id'))
    to_location_id = Column(Integer, ForeignKey('locations.id'))
    
    # Tracking
    lot_id = Column(Integer, ForeignKey('lots.id'))
    serial_id = Column(Integer, ForeignKey('serials.id'))
    
    # Cost (for receipts)
    unit_cost = Column(Numeric(18, 4))
    total_cost = Column(Numeric(18, 2))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    header = relationship('DocumentHeader', back_populates='lines')
    item = relationship('Item')
    uom = relationship('UOM')
    from_location = relationship('Location', foreign_keys=[from_location_id])
    to_location = relationship('Location', foreign_keys=[to_location_id])
    lot = relationship('Lot')
    serial = relationship('Serial')
    
    __table_args__ = (
        Index('idx_docline_header', 'header_id'),
        Index('idx_docline_item', 'item_id'),
    )
    
    def __repr__(self):
        return f"<DocumentLine(id={self.id}, header_id={self.header_id}, line_no={self.line_no}, item_id={self.item_id})>"


class InventoryLedger(Base):
    __tablename__ = 'inventory_ledger'
    
    id = Column(Integer, primary_key=True)
    
    # Posting info
    posting_date = Column(Date, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    
    # Item
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    
    # Quantity (Base UOM)
    qty_in = Column(Numeric(18, 4), default=0)
    qty_out = Column(Numeric(18, 4), default=0)
    
    # Cost and value
    unit_cost = Column(Numeric(18, 4))
    value_in = Column(Numeric(18, 2), default=0)
    value_out = Column(Numeric(18, 2), default=0)
    
    # Tracking
    lot_id = Column(Integer, ForeignKey('lots.id'))
    serial_id = Column(Integer, ForeignKey('serials.id'))
    
    # Document reference
    doc_type = Column(Enum(DocumentType), nullable=False)
    doc_id = Column(Integer, ForeignKey('documents_header.id'), nullable=False)
    doc_no = Column(String(50), nullable=False)
    line_no = Column(Integer, nullable=False)
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship('Item')
    warehouse = relationship('Warehouse')
    location = relationship('Location')
    lot = relationship('Lot')
    serial = relationship('Serial')
    document = relationship('DocumentHeader')
    
    __table_args__ = (
        Index('idx_ledger_posting_date', 'posting_date'),
        Index('idx_ledger_company_item', 'company_id', 'item_id'),
        Index('idx_ledger_warehouse_item', 'warehouse_id', 'item_id'),
        Index('idx_ledger_doc', 'doc_type', 'doc_id'),
    )
    
    def __repr__(self):
        return f"<InventoryLedger(id={self.id}, posting_date={self.posting_date}, item_id={self.item_id}, qty_in={self.qty_in}, qty_out={self.qty_out})>"


class StockBalance(Base):
    __tablename__ = 'stock_balance'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    
    # Tracking
    lot_id = Column(Integer, ForeignKey('lots.id'))
    serial_id = Column(Integer, ForeignKey('serials.id'))
    
    # Balance
    on_hand_qty = Column(Numeric(18, 4), default=0)
    on_hand_value = Column(Numeric(18, 2), default=0)
    avg_cost = Column(Numeric(18, 4), default=0)
    
    # Last update
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship('Item')
    warehouse = relationship('Warehouse')
    location = relationship('Location')
    lot = relationship('Lot')
    serial = relationship('Serial')
    
    __table_args__ = (
        Index('idx_balance_company_item', 'company_id', 'item_id'),
        Index('idx_balance_warehouse_item', 'warehouse_id', 'item_id'),
        Index('idx_balance_location_item', 'location_id', 'item_id'),
    )
    
    def __repr__(self):
        return f"<StockBalance(id={self.id}, warehouse_id={self.warehouse_id}, item_id={self.item_id}, on_hand_qty={self.on_hand_qty})>"


class StockCount(Base):
    __tablename__ = 'stock_counts'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    count_no = Column(String(50), nullable=False)
    count_date = Column(Date, nullable=False)
    
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    notes = Column(Text)
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_by = Column(Integer, ForeignKey('users.id'))
    posted_at = Column(DateTime)
    
    # Relationships
    warehouse = relationship('Warehouse')
    lines = relationship('StockCountLine', back_populates='count', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<StockCount(id={self.id}, count_no='{self.count_no}', status='{self.status}')>"


class StockCountLine(Base):
    __tablename__ = 'stock_count_lines'
    
    id = Column(Integer, primary_key=True)
    count_id = Column(Integer, ForeignKey('stock_counts.id'), nullable=False)
    line_no = Column(Integer, nullable=False)
    
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    lot_id = Column(Integer, ForeignKey('lots.id'))
    serial_id = Column(Integer, ForeignKey('serials.id'))
    
    # Quantities
    system_qty = Column(Numeric(18, 4), default=0)
    counted_qty = Column(Numeric(18, 4), default=0)
    variance_qty = Column(Numeric(18, 4), default=0)
    
    notes = Column(Text)
    
    # Relationships
    count = relationship('StockCount', back_populates='lines')
    item = relationship('Item')
    location = relationship('Location')
    lot = relationship('Lot')
    serial = relationship('Serial')
    
    def __repr__(self):
        return f"<StockCountLine(id={self.id}, count_id={self.count_id}, item_id={self.item_id}, variance_qty={self.variance_qty})>"
