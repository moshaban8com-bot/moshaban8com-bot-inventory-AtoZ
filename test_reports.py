"""
Test reports and Excel export
اختبار التقارير والتصدير
"""

from datetime import date
from pathlib import Path

from data import session_scope, init_db
from reports import InventoryReports
from import_export import ExcelExporter
from utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger('test_reports')


def test_reports():
    """Test inventory reports"""
    logger.info('اختبار التقارير...')
    
    init_db()
    
    with session_scope() as session:
        company_id = 1
        
        # Test stock on hand
        logger.info('تقرير الأرصدة الحالية:')
        stock = InventoryReports.stock_on_hand(session, company_id)
        for item in stock:
            logger.info(f"  {item['item_name_ar']}: {item['qty']} {item['uom']}")
        
        # Test inventory valuation
        logger.info('\nملخص قيمة المخزون:')
        valuation = InventoryReports.inventory_valuation(session, company_id)
        logger.info(f"  عدد الأصناف: {valuation['item_count']}")
        logger.info(f"  إجمالي القيمة: {valuation['total_value']:.2f}")
        
        # Test movement summary
        logger.info('\nملخص الحركة:')
        movements = InventoryReports.movement_summary(
            session, company_id,
            from_date=date(2024, 1, 1),
            to_date=date.today()
        )
        for mov in movements:
            logger.info(f"  {mov['item_name_ar']}: وارد {mov['qty_in']}, صادر {mov['qty_out']}")
        
        # Export to Excel
        logger.info('\nتصدير إلى Excel...')
        
        if stock:
            headers = {
                'item_code': 'كود الصنف',
                'item_name_ar': 'اسم الصنف',
                'warehouse': 'المخزن',
                'qty': 'الكمية',
                'avg_cost': 'متوسط التكلفة',
                'value': 'القيمة'
            }
            
            output_dir = Path('/tmp')
            output_dir.mkdir(exist_ok=True)
            
            excel_file = output_dir / 'stock_report.xlsx'
            ExcelExporter.save_excel_file(
                str(excel_file),
                stock,
                headers,
                title='تقرير الأرصدة الحالية',
                sheet_name='الأرصدة'
            )
            logger.info(f'✅ تم حفظ ملف Excel: {excel_file}')
            
            # Also save as CSV
            csv_file = output_dir / 'stock_report.csv'
            ExcelExporter.save_csv_file(str(csv_file), stock, headers)
            logger.info(f'✅ تم حفظ ملف CSV: {csv_file}')


if __name__ == '__main__':
    test_reports()
