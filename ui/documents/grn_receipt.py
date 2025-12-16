"""
GRN Receipt Screen - شاشة استلام البضاعة
"""

from PySide6.QtWidgets import QFormLayout, QGroupBox
from PySide6.QtCore import Qt

from data.models import DocumentType
from ui.documents.base_document import BaseDocumentScreen
from ui.widgets import ComboSearchWidget
from data import session_scope, Supplier
from utils.logging import get_logger

logger = get_logger('grn_receipt')


class GRNReceiptScreen(BaseDocumentScreen):
    """GRN (Goods Receipt Note) document screen"""
    
    def __init__(self, company_id, warehouse_id, parent=None):
        super().__init__(company_id, warehouse_id, DocumentType.GRN_RECEIPT, parent)
        
        self.title_label.setText('استلام بضاعة / GRN Receipt')
        
    def create_header_section(self):
        """Create GRN-specific header section"""
        group = QGroupBox('معلومات الاستلام / Receipt Information')
        layout = QFormLayout(group)
        
        # Document Number
        self.doc_number_label = self.create_label('سيتم إنشاؤه تلقائياً / Auto-generated')
        layout.addRow('رقم المستند / Doc Number:', self.doc_number_label)
        
        # Date
        from ui.widgets import DatePickerWidget
        self.date_picker = DatePickerWidget()
        layout.addRow('التاريخ / Date *:', self.date_picker)
        
        # Supplier
        self.supplier_combo = ComboSearchWidget()
        self.load_suppliers()
        layout.addRow('المورد / Supplier *:', self.supplier_combo)
        
        # Warehouse (read-only, from parent)
        self.warehouse_label = self.create_label(f'المخزن: {self.warehouse_id}')
        layout.addRow('المخزن / Warehouse:', self.warehouse_label)
        
        # Reference Number
        from PySide6.QtWidgets import QLineEdit
        self.reference_edit = QLineEdit()
        self.reference_edit.setPlaceholderText('رقم مرجعي اختياري...')
        layout.addRow('الرقم المرجعي / Reference:', self.reference_edit)
        
        # Notes
        from PySide6.QtWidgets import QTextEdit
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText('ملاحظات اختيارية...')
        layout.addRow('ملاحظات / Notes:', self.notes_edit)
        
        return group
        
    def create_label(self, text):
        """Helper to create a label"""
        from PySide6.QtWidgets import QLabel
        label = QLabel(text)
        return label
        
    def load_suppliers(self):
        """Load suppliers for the combo box"""
        try:
            with session_scope() as session:
                suppliers = session.query(Supplier).filter_by(
                    company_id=self.company_id,
                    is_active=True
                ).all()
                
                for supplier in suppliers:
                    self.supplier_combo.add_item(
                        f'{supplier.code} - {supplier.name_ar}',
                        supplier.id
                    )
                    
                logger.info(f'Loaded {len(suppliers)} suppliers')
                
        except Exception as e:
            logger.error(f'Error loading suppliers: {str(e)}', exc_info=True)
            
    def create_lines_section(self):
        """Create GRN-specific lines section"""
        group = super().create_lines_section()
        
        # Update column headers for GRN
        self.lines_table.setColumnCount(7)
        self.lines_table.setHorizontalHeaderLabels([
            'كود الصنف / Item Code',
            'اسم الصنف / Item Name',
            'الوحدة / UOM',
            'الكمية / Quantity',
            'السعر / Unit Price',
            'الإجمالي / Total',
            'ملاحظات / Notes'
        ])
        
        return group
        
    def save_document(self):
        """Save GRN document"""
        # Validate
        if not self.supplier_combo.get_selected_data():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'الرجاء اختيار المورد\nPlease select supplier'
            )
            return
            
        if self.lines_table.rowCount() == 0:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'الرجاء إضافة أصناف\nPlease add items'
            )
            return
        
        # TODO: Save to database
        logger.info('Saving GRN document...')
        logger.info(f'Supplier: {self.supplier_combo.get_selected_data()}')
        logger.info(f'Date: {self.date_picker.get_date_string()}')
        logger.info(f'Reference: {self.reference_edit.text()}')
        logger.info(f'Lines: {self.lines_table.rowCount()}')
        
        super().save_document()
        
    def post_document(self):
        """Post GRN document"""
        # TODO: Implement posting logic using PostingService
        logger.info('Posting GRN document...')
        
        super().post_document()
