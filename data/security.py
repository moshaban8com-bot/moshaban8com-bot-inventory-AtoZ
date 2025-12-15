"""
Security models: Users, Roles, Permissions, and Audit
نماذج الأمان: المستخدمون والأدوار والصلاحيات والمراجعة
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship

from data.database import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name_ar = Column(String(200), nullable=False)
    full_name_en = Column(String(200), nullable=False)
    email = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Login tracking
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship('UserRole', back_populates='user')
    company_access = relationship('UserCompanyAccess', back_populates='user')
    warehouse_access = relationship('UserWarehouseAccess', back_populates='user')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name_ar='{self.full_name_ar}')>"


class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = relationship('RolePermission', back_populates='role')
    users = relationship('UserRole', back_populates='role')
    
    def __repr__(self):
        return f"<Role(id={self.id}, code='{self.code}', name_ar='{self.name_ar}')>"


class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    module = Column(String(50), nullable=False)  # INVENTORY, MANUFACTURING, etc.
    resource = Column(String(100), nullable=False)  # ITEMS, DOCUMENTS, etc.
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, POST, APPROVE
    
    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', module='{self.module}')>"


class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    
    # Relationships
    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission')
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class UserRole(Base):
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='roles')
    role = relationship('Role', back_populates='users')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class UserCompanyAccess(Base):
    __tablename__ = 'user_company_access'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='company_access')
    company = relationship('Company')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='uq_user_company'),
    )
    
    def __repr__(self):
        return f"<UserCompanyAccess(user_id={self.user_id}, company_id={self.company_id})>"


class UserWarehouseAccess(Base):
    __tablename__ = 'user_warehouse_access'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='warehouse_access')
    warehouse = relationship('Warehouse')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'warehouse_id', name='uq_user_warehouse'),
    )
    
    def __repr__(self):
        return f"<UserWarehouseAccess(user_id={self.user_id}, warehouse_id={self.warehouse_id})>"


class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))  # Nullable for failed logins
    company_id = Column(Integer, ForeignKey('companies.id'))
    
    # Action details
    action = Column(String(50), nullable=False)  # LOGIN, CREATE, UPDATE, DELETE, POST, APPROVE, OVERRIDE
    entity_type = Column(String(100))  # Table name or entity type
    entity_id = Column(Integer)
    
    # Changes
    before_value = Column(Text)  # JSON
    after_value = Column(Text)  # JSON
    
    # Additional context
    description = Column(Text)
    ip_address = Column(String(45))
    
    # Relationships
    user = relationship('User')
    
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', timestamp={self.timestamp})>"
