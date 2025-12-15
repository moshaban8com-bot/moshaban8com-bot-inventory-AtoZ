"""
Data package - Database models and ORM
حزمة البيانات - نماذج قاعدة البيانات
"""

from data.database import (
    Base,
    init_db,
    get_engine,
    get_session,
    session_scope,
    create_all_tables,
    drop_all_tables
)

from data.models import (
    DocumentStatus, DocumentType, ItemType, TrackingType, PolicyScope,
    Company, CompanyModule, Warehouse, Location,
    ItemCategory, UOM, Item, ItemUOMConversion, Barcode,
    Supplier, Customer, ReasonCode,
    Lot, Serial
)

from data.documents import (
    DocumentSequence, DocumentHeader, DocumentLine,
    InventoryLedger, StockBalance,
    StockCount, StockCountLine
)

from data.security import (
    User, Role, Permission, RolePermission, UserRole,
    UserCompanyAccess, UserWarehouseAccess, AuditLog
)

from data.policies import (
    Policy,
    BOM, BOMLine,
    WorkCenter, Routing, RoutingStep,
    ProductionOrder, ProductionIssue, ProductionReceipt, ScrapDocument
)

__all__ = [
    # Database utilities
    'Base', 'init_db', 'get_engine', 'get_session', 'session_scope',
    'create_all_tables', 'drop_all_tables',
    
    # Enums
    'DocumentStatus', 'DocumentType', 'ItemType', 'TrackingType', 'PolicyScope',
    
    # Core models
    'Company', 'CompanyModule', 'Warehouse', 'Location',
    'ItemCategory', 'UOM', 'Item', 'ItemUOMConversion', 'Barcode',
    'Supplier', 'Customer', 'ReasonCode',
    'Lot', 'Serial',
    
    # Documents
    'DocumentSequence', 'DocumentHeader', 'DocumentLine',
    'InventoryLedger', 'StockBalance',
    'StockCount', 'StockCountLine',
    
    # Security
    'User', 'Role', 'Permission', 'RolePermission', 'UserRole',
    'UserCompanyAccess', 'UserWarehouseAccess', 'AuditLog',
    
    # Policies and Manufacturing
    'Policy',
    'BOM', 'BOMLine',
    'WorkCenter', 'Routing', 'RoutingStep',
    'ProductionOrder', 'ProductionIssue', 'ProductionReceipt', 'ScrapDocument',
]
