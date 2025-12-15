"""
Policy and Manufacturing models
نماذج السياسات والتصنيع
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Boolean, Numeric,
    ForeignKey, Text, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship

from data.database import Base
from data.models import PolicyScope


class Policy(Base):
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True)
    
    # Scope
    scope_type = Column(Enum(PolicyScope), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    doc_type = Column(String(50))  # For DOCTYPE scope
    category_id = Column(Integer, ForeignKey('item_categories.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    
    # Policy details
    policy_name = Column(String(100), nullable=False)  # e.g., BLOCK_NEGATIVE_STOCK
    policy_value = Column(Boolean, default=True)
    
    # Override settings
    override_allowed = Column(Boolean, default=False)
    override_requires_approval = Column(Boolean, default=False)
    approval_role_id = Column(Integer, ForeignKey('roles.id'))
    reason_required = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company')
    warehouse = relationship('Warehouse')
    category = relationship('ItemCategory')
    item = relationship('Item')
    approval_role = relationship('Role')
    
    __table_args__ = (
        Index('idx_policy_scope', 'scope_type', 'company_id', 'warehouse_id'),
    )
    
    def __repr__(self):
        return f"<Policy(id={self.id}, scope='{self.scope_type}', policy='{self.policy_name}', value={self.policy_value})>"


# ============= Manufacturing Models =============

class BOM(Base):
    __tablename__ = 'boms'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)  # Finished good
    bom_no = Column(String(50), nullable=False)
    version = Column(Integer, default=1)
    
    # Validity
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    # Production details
    base_qty = Column(Numeric(18, 4), default=1)  # Quantity produced
    uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    
    # Costing
    estimated_cost = Column(Numeric(18, 2))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship('Item')
    uom = relationship('UOM')
    lines = relationship('BOMLine', back_populates='bom', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'bom_no', name='uq_bom_no'),
    )
    
    def __repr__(self):
        return f"<BOM(id={self.id}, bom_no='{self.bom_no}', item_id={self.item_id}, version={self.version})>"


class BOMLine(Base):
    __tablename__ = 'bom_lines'
    
    id = Column(Integer, primary_key=True)
    bom_id = Column(Integer, ForeignKey('boms.id'), nullable=False)
    line_no = Column(Integer, nullable=False)
    
    # Component item
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    qty = Column(Numeric(18, 4), nullable=False)
    uom_id = Column(Integer, ForeignKey('uoms.id'), nullable=False)
    base_qty = Column(Numeric(18, 4), nullable=False)
    
    # Scrap/Waste allowance
    scrap_percent = Column(Numeric(5, 2), default=0)
    
    # Operation (optional)
    operation_seq = Column(Integer)
    
    notes = Column(Text)
    
    # Relationships
    bom = relationship('BOM', back_populates='lines')
    item = relationship('Item')
    uom = relationship('UOM')
    
    def __repr__(self):
        return f"<BOMLine(id={self.id}, bom_id={self.bom_id}, item_id={self.item_id}, qty={self.qty})>"


class WorkCenter(Base):
    __tablename__ = 'work_centers'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(20), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    
    # Capacity
    capacity_per_day = Column(Numeric(18, 2))
    cost_per_hour = Column(Numeric(18, 2))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_workcenter_code'),
    )
    
    def __repr__(self):
        return f"<WorkCenter(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class Routing(Base):
    __tablename__ = 'routings'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    bom_id = Column(Integer, ForeignKey('boms.id'), nullable=False)
    routing_no = Column(String(50), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bom = relationship('BOM')
    steps = relationship('RoutingStep', back_populates='routing', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'routing_no', name='uq_routing_no'),
    )
    
    def __repr__(self):
        return f"<Routing(id={self.id}, routing_no='{self.routing_no}', bom_id={self.bom_id})>"


class RoutingStep(Base):
    __tablename__ = 'routing_steps'
    
    id = Column(Integer, primary_key=True)
    routing_id = Column(Integer, ForeignKey('routings.id'), nullable=False)
    step_no = Column(Integer, nullable=False)
    work_center_id = Column(Integer, ForeignKey('work_centers.id'), nullable=False)
    
    operation_name = Column(String(200), nullable=False)
    setup_time = Column(Numeric(18, 2))  # Hours
    run_time = Column(Numeric(18, 2))  # Hours per unit
    
    notes = Column(Text)
    
    # Relationships
    routing = relationship('Routing', back_populates='steps')
    work_center = relationship('WorkCenter')
    
    def __repr__(self):
        return f"<RoutingStep(id={self.id}, routing_id={self.routing_id}, step_no={self.step_no})>"


class ProductionOrder(Base):
    __tablename__ = 'production_orders'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    
    po_no = Column(String(50), nullable=False)
    po_date = Column(Date, nullable=False)
    
    # Item to produce
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    bom_id = Column(Integer, ForeignKey('boms.id'), nullable=False)
    
    # Quantities
    planned_qty = Column(Numeric(18, 4), nullable=False)
    produced_qty = Column(Numeric(18, 4), default=0)
    scrap_qty = Column(Numeric(18, 4), default=0)
    
    # Status
    status = Column(String(20), default='DRAFT')  # DRAFT, RELEASED, IN_PROGRESS, COMPLETED, CANCELLED
    
    # Dates
    start_date = Column(Date)
    completion_date = Column(Date)
    
    notes = Column(Text)
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    warehouse = relationship('Warehouse')
    item = relationship('Item')
    bom = relationship('BOM')
    
    __table_args__ = (
        UniqueConstraint('company_id', 'po_no', name='uq_po_no'),
    )
    
    def __repr__(self):
        return f"<ProductionOrder(id={self.id}, po_no='{self.po_no}', item_id={self.item_id}, status='{self.status}')>"


class ProductionIssue(Base):
    __tablename__ = 'production_issues'
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey('production_orders.id'), nullable=False)
    doc_id = Column(Integer, ForeignKey('documents_header.id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = relationship('ProductionOrder')
    document = relationship('DocumentHeader')
    
    def __repr__(self):
        return f"<ProductionIssue(id={self.id}, production_order_id={self.production_order_id}, doc_id={self.doc_id})>"


class ProductionReceipt(Base):
    __tablename__ = 'production_receipts'
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey('production_orders.id'), nullable=False)
    doc_id = Column(Integer, ForeignKey('documents_header.id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = relationship('ProductionOrder')
    document = relationship('DocumentHeader')
    
    def __repr__(self):
        return f"<ProductionReceipt(id={self.id}, production_order_id={self.production_order_id}, doc_id={self.doc_id})>"


class ScrapDocument(Base):
    __tablename__ = 'scrap_docs'
    
    id = Column(Integer, primary_key=True)
    production_order_id = Column(Integer, ForeignKey('production_orders.id'))
    doc_id = Column(Integer, ForeignKey('documents_header.id'), nullable=False)
    
    scrap_type = Column(String(20), default='PRODUCTION')  # PRODUCTION, GENERAL
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = relationship('ProductionOrder')
    document = relationship('DocumentHeader')
    
    def __repr__(self):
        return f"<ScrapDocument(id={self.id}, doc_id={self.doc_id}, scrap_type='{self.scrap_type}')>"
