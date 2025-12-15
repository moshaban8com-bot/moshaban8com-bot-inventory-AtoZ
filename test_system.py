"""
Simple test script to verify core functionality
اختبار بسيط للتحقق من الوظائف الأساسية
"""

from datetime import date
from decimal import Decimal

from data import (
    session_scope, init_db,
    Company, Warehouse, Item, DocumentHeader, DocumentLine,
    DocumentType, DocumentStatus, UOM
)
from security.auth import auth_service
from services import PostingService, CostingService
from utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger('test')

def test_authentication():
    """Test user authentication"""
    logger.info('اختبار المصادقة...')
    
    try:
        # Login with demo credentials
        user = auth_service.login('admin', 'admin123')
        logger.info(f'✅ تسجيل الدخول نجح: {user.full_name_ar}')
        
        # Check session is valid
        if auth_service.is_session_valid():
            logger.info('✅ الجلسة صالحة')
        
        # Set company and warehouse
        auth_service.set_current_company(1)
        auth_service.set_current_warehouse(1)
        logger.info(f'✅ تم تعيين الشركة والمخزن')
        
        # Logout
        auth_service.logout()
        logger.info('✅ تسجيل الخروج نجح')
        
        return True
    except Exception as e:
        logger.error(f'❌ فشل اختبار المصادقة: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_document_posting():
    """Test document creation and posting"""
    logger.info('اختبار إنشاء وترحيل المستندات...')
    
    try:
        # Create document first
        doc_id = None
        with session_scope() as session:
            # Get company, warehouse, and item
            company = session.query(Company).first()
            warehouse = session.query(Warehouse).first()
            item = session.query(Item).first()
            uom = session.query(UOM).filter_by(code='PCS').first()
            
            # Create a receipt document
            doc = DocumentHeader(
                company_id=company.id,
                doc_type=DocumentType.GRN_RECEIPT,
                doc_no='GRN-TEST-002',
                doc_date=date.today(),
                to_warehouse_id=warehouse.id,
                status=DocumentStatus.DRAFT,
                created_by=1
            )
            session.add(doc)
            session.flush()
            
            # Add a line
            line = DocumentLine(
                header_id=doc.id,
                line_no=1,
                item_id=item.id,
                qty=Decimal('100'),
                uom_id=uom.id,
                base_qty=Decimal('100'),
                unit_cost=Decimal('10.50'),
                total_cost=Decimal('1050.00')
            )
            session.add(line)
            session.commit()
            
            doc_id = doc.id
            logger.info(f'✅ تم إنشاء مستند: GRN-TEST-002')
        
        # Post the document in a separate transaction
        posting_service = PostingService()
        result = posting_service.post_document(doc_id, user_id=1)
        
        logger.info(f'✅ تم ترحيل المستند')
        
        # Verify in another session
        with session_scope() as session:
            company = session.query(Company).first()
            warehouse = session.query(Warehouse).first()
            item = session.query(Item).first()
            
            # Verify stock balance
            costing_service = CostingService()
            avg_cost = costing_service.get_average_cost(
                session=session,
                company_id=company.id,
                warehouse_id=warehouse.id,
                item_id=item.id
            )
            
            logger.info(f'✅ متوسط التكلفة: {avg_cost}')
        
        return True
            
    except Exception as e:
        logger.error(f'❌ فشل اختبار الترحيل: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_costing():
    """Test costing calculations"""
    logger.info('اختبار حساب التكلفة...')
    
    try:
        with session_scope() as session:
            company = session.query(Company).first()
            warehouse = session.query(Warehouse).first()
            
            costing_service = CostingService()
            total_value = costing_service.calculate_total_value(
                session=session,
                company_id=company.id,
                warehouse_id=warehouse.id
            )
            
            logger.info(f'✅ إجمالي قيمة المخزون: {total_value}')
            
            return True
            
    except Exception as e:
        logger.error(f'❌ فشل اختبار التكلفة: {e}')
        return False


def main():
    """Run all tests"""
    logger.info('=' * 60)
    logger.info('بدء اختبارات النظام')
    logger.info('=' * 60)
    
    # Initialize database
    init_db()
    
    # Run tests
    results = []
    
    results.append(('المصادقة', test_authentication()))
    results.append(('الترحيل', test_document_posting()))
    results.append(('التكلفة', test_costing()))
    
    # Print summary
    logger.info('=' * 60)
    logger.info('ملخص النتائج:')
    logger.info('=' * 60)
    
    for test_name, result in results:
        status = '✅ نجح' if result else '❌ فشل'
        logger.info(f'{test_name}: {status}')
    
    total_passed = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    logger.info('=' * 60)
    logger.info(f'النتيجة النهائية: {total_passed}/{total_tests} اختبارات نجحت')
    logger.info('=' * 60)


if __name__ == '__main__':
    main()
