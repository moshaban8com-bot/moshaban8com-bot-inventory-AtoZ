"""
Seed data for demo/testing
بيانات تجريبية للنظام
"""

from datetime import date
from decimal import Decimal

from data import (
    session_scope, create_all_tables,
    Company, CompanyModule, Warehouse, Location,
    UOM, ItemCategory, Item,
    User, Role, Permission, RolePermission, UserRole,
    UserCompanyAccess, UserWarehouseAccess,
    PolicyScope, Policy
)
from security.auth import AuthService
from utils.dates import get_fiscal_year_dates
from utils.logging import get_logger

logger = get_logger('seed')


def seed_database():
    """Create demo data for the system"""
    logger.info('بدء إنشاء البيانات التجريبية...')
    
    # Create tables
    logger.info('إنشاء جداول قاعدة البيانات...')
    create_all_tables()
    
    with session_scope() as session:
        # Create demo company
        logger.info('إنشاء شركة تجريبية...')
        start_date, end_date = get_fiscal_year_dates(2024, 1)
        
        company = Company(
            code='DEMO',
            name_ar='شركة تجريبية',
            name_en='Demo Company',
            currency='EGP',
            fiscal_year_start=start_date,
            fiscal_year_end=end_date,
            is_active=True
        )
        session.add(company)
        session.flush()
        
        # Enable modules
        logger.info('تفعيل الوحدات...')
        modules = ['INVENTORY', 'MANUFACTURING']
        for module_name in modules:
            module = CompanyModule(
                company_id=company.id,
                module_name=module_name,
                is_enabled=True
            )
            session.add(module)
        
        # Create warehouses
        logger.info('إنشاء المخازن...')
        main_warehouse = Warehouse(
            company_id=company.id,
            code='WH01',
            name_ar='المخزن الرئيسي',
            name_en='Main Warehouse',
            is_active=True
        )
        session.add(main_warehouse)
        session.flush()
        
        # Create locations
        logger.info('إنشاء المواقع...')
        location = Location(
            warehouse_id=main_warehouse.id,
            code='A-01-01',
            zone='A',
            rack='01',
            shelf='01',
            is_active=True
        )
        session.add(location)
        
        # Create UOMs
        logger.info('إنشاء وحدات القياس...')
        uoms_data = [
            ('PCS', 'قطعة', 'Piece'),
            ('BOX', 'صندوق', 'Box'),
            ('KG', 'كيلوجرام', 'Kilogram'),
            ('M', 'متر', 'Meter'),
        ]
        uoms = {}
        for code, name_ar, name_en in uoms_data:
            uom = UOM(code=code, name_ar=name_ar, name_en=name_en)
            session.add(uom)
            session.flush()
            uoms[code] = uom
        
        # Create item categories
        logger.info('إنشاء تصنيفات الأصناف...')
        category = ItemCategory(
            company_id=company.id,
            code='RAW',
            name_ar='مواد خام',
            name_en='Raw Materials',
            is_active=True
        )
        session.add(category)
        session.flush()
        
        # Create sample items
        logger.info('إنشاء أصناف تجريبية...')
        item1 = Item(
            company_id=company.id,
            code='ITEM001',
            name_ar='صنف تجريبي 1',
            name_en='Demo Item 1',
            category_id=category.id,
            base_uom_id=uoms['PCS'].id,
            min_qty=Decimal('10'),
            max_qty=Decimal('1000'),
            reorder_point=Decimal('50'),
            is_active=True
        )
        session.add(item1)
        
        item2 = Item(
            company_id=company.id,
            code='ITEM002',
            name_ar='صنف تجريبي 2',
            name_en='Demo Item 2',
            category_id=category.id,
            base_uom_id=uoms['KG'].id,
            min_qty=Decimal('5'),
            max_qty=Decimal('500'),
            reorder_point=Decimal('25'),
            is_active=True
        )
        session.add(item2)
        
        # Create roles
        logger.info('إنشاء الأدوار...')
        admin_role = Role(
            code='ADMIN',
            name_ar='مدير النظام',
            name_en='System Administrator',
            description='Full system access',
            is_active=True
        )
        session.add(admin_role)
        
        warehouse_role = Role(
            code='WAREHOUSE',
            name_ar='أمين مخزن',
            name_en='Warehouse Keeper',
            description='Warehouse operations',
            is_active=True
        )
        session.add(warehouse_role)
        session.flush()
        
        # Create permissions
        logger.info('إنشاء الصلاحيات...')
        permissions_data = [
            ('ITEMS.CREATE', 'إنشاء صنف', 'Create Item', 'INVENTORY', 'ITEMS', 'CREATE'),
            ('ITEMS.READ', 'عرض الأصناف', 'View Items', 'INVENTORY', 'ITEMS', 'READ'),
            ('ITEMS.UPDATE', 'تعديل صنف', 'Update Item', 'INVENTORY', 'ITEMS', 'UPDATE'),
            ('DOCS.CREATE', 'إنشاء مستند', 'Create Document', 'INVENTORY', 'DOCUMENTS', 'CREATE'),
            ('DOCS.POST', 'ترحيل مستند', 'Post Document', 'INVENTORY', 'DOCUMENTS', 'POST'),
        ]
        
        permissions = []
        for code, name_ar, name_en, module, resource, action in permissions_data:
            perm = Permission(
                code=code,
                name_ar=name_ar,
                name_en=name_en,
                module=module,
                resource=resource,
                action=action
            )
            session.add(perm)
            permissions.append(perm)
        
        session.flush()
        
        # Assign permissions to admin role
        for perm in permissions:
            role_perm = RolePermission(
                role_id=admin_role.id,
                permission_id=perm.id
            )
            session.add(role_perm)
        
        # Create admin user
        logger.info('إنشاء مستخدم المدير...')
        auth_service = AuthService()
        password_hash = auth_service.hash_password('admin123')
        
        admin_user = User(
            username='admin',
            password_hash=password_hash,
            full_name_ar='المدير',
            full_name_en='Administrator',
            email='admin@demo.com',
            is_active=True,
            is_admin=True
        )
        session.add(admin_user)
        session.flush()
        
        # Assign role to user
        user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id
        )
        session.add(user_role)
        
        # Grant company access
        company_access = UserCompanyAccess(
            user_id=admin_user.id,
            company_id=company.id,
            is_default=True
        )
        session.add(company_access)
        
        # Grant warehouse access
        warehouse_access = UserWarehouseAccess(
            user_id=admin_user.id,
            warehouse_id=main_warehouse.id,
            is_default=True
        )
        session.add(warehouse_access)
        
        # Create global policies
        logger.info('إنشاء السياسات...')
        policies_data = [
            ('BLOCK_NEGATIVE_STOCK', True),
            ('LOCK_POSTED_DOCUMENTS', True),
            ('REQUIRE_REASON_CODE_FOR_ADJUSTMENTS', True),
        ]
        
        for policy_name, policy_value in policies_data:
            policy = Policy(
                scope_type=PolicyScope.GLOBAL,
                policy_name=policy_name,
                policy_value=policy_value
            )
            session.add(policy)
        
        session.commit()
    
    logger.info('تم إنشاء البيانات التجريبية بنجاح!')
    logger.info('معلومات تسجيل الدخول:')
    logger.info('  اسم المستخدم: admin')
    logger.info('  كلمة المرور: admin123')


if __name__ == '__main__':
    from utils.logging import setup_logging
    setup_logging()
    seed_database()
