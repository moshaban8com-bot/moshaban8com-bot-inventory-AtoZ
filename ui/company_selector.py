"""
Company and Warehouse Selector Dialog
مربع حوار اختيار الشركة والمخزن
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal

from data import session_scope, Company, Warehouse
from utils.logging import get_logger

logger = get_logger('company_selector')


class CompanySelectorDialog(QDialog):
    """Dialog for selecting company and warehouse"""
    
    # Signals
    selection_confirmed = Signal(int, int)  # company_id, warehouse_id
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.selected_company_id = None
        self.selected_warehouse_id = None
        
        self.setup_ui()
        self.load_companies()
        
        self.setWindowTitle('اختيار الشركة والمخزن - Select Company & Warehouse')
        self.setModal(True)
        self.setMinimumWidth(500)
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(f'مرحباً {self.user.full_name_ar}')
        title_label.setProperty('heading', True)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel('الرجاء اختيار الشركة والمخزن للعمل عليهما')
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet('color: #64748b;')
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(10)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        layout.addSpacing(20)
        
        # Company selection
        company_label = QLabel('الشركة / Company')
        layout.addWidget(company_label)
        
        self.company_combo = QComboBox()
        self.company_combo.currentIndexChanged.connect(self.on_company_changed)
        layout.addWidget(self.company_combo)
        
        layout.addSpacing(15)
        
        # Warehouse selection
        warehouse_label = QLabel('المخزن / Warehouse')
        layout.addWidget(warehouse_label)
        
        self.warehouse_combo = QComboBox()
        layout.addWidget(self.warehouse_combo)
        
        layout.addSpacing(15)
        
        # Save as default checkbox
        self.save_default_checkbox = QCheckBox(
            'حفظ كاختيار افتراضي / Save as default'
        )
        layout.addWidget(self.save_default_checkbox)
        
        layout.addSpacing(20)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton('إلغاء / Cancel')
        self.cancel_button.setProperty('secondary', True)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.confirm_button = QPushButton('تأكيد / Confirm')
        self.confirm_button.setDefault(True)
        self.confirm_button.clicked.connect(self.on_confirm)
        buttons_layout.addWidget(self.confirm_button)
        
        layout.addLayout(buttons_layout)
        
    def load_companies(self):
        """Load companies accessible by the user"""
        try:
            with session_scope() as session:
                # Get all active companies
                # TODO: Filter by user permissions when implemented
                companies = session.query(Company).filter_by(is_active=True).all()
                
                if not companies:
                    QMessageBox.warning(
                        self,
                        'تحذير - Warning',
                        'لا توجد شركات نشطة\nNo active companies found'
                    )
                    return
                
                # Populate combo box
                for company in companies:
                    self.company_combo.addItem(
                        f'{company.name_ar} - {company.name_en}',
                        company.id
                    )
                
                # Load warehouses for first company
                if self.company_combo.count() > 0:
                    self.on_company_changed(0)
                    
        except Exception as e:
            logger.error(f'خطأ في تحميل الشركات: {str(e)}', exc_info=True)
            QMessageBox.critical(
                self,
                'خطأ - Error',
                f'حدث خطأ أثناء تحميل الشركات\nError loading companies:\n{str(e)}'
            )
    
    def on_company_changed(self, index):
        """Handle company selection change"""
        if index < 0:
            return
        
        company_id = self.company_combo.currentData()
        if not company_id:
            return
        
        self.load_warehouses(company_id)
    
    def load_warehouses(self, company_id: int):
        """Load warehouses for selected company"""
        try:
            self.warehouse_combo.clear()
            
            with session_scope() as session:
                warehouses = session.query(Warehouse).filter_by(
                    company_id=company_id,
                    is_active=True
                ).all()
                
                if not warehouses:
                    QMessageBox.warning(
                        self,
                        'تحذير - Warning',
                        'لا توجد مخازن نشطة لهذه الشركة\n'
                        'No active warehouses found for this company'
                    )
                    return
                
                # Populate combo box
                for warehouse in warehouses:
                    self.warehouse_combo.addItem(
                        f'{warehouse.name_ar} - {warehouse.name_en}',
                        warehouse.id
                    )
                    
        except Exception as e:
            logger.error(f'خطأ في تحميل المخازن: {str(e)}', exc_info=True)
            QMessageBox.critical(
                self,
                'خطأ - Error',
                f'حدث خطأ أثناء تحميل المخازن\nError loading warehouses:\n{str(e)}'
            )
    
    def on_confirm(self):
        """Handle confirm button click"""
        # Validate selections
        if self.company_combo.currentIndex() < 0:
            QMessageBox.warning(
                self,
                'تحذير - Warning',
                'الرجاء اختيار شركة\nPlease select a company'
            )
            return
        
        if self.warehouse_combo.currentIndex() < 0:
            QMessageBox.warning(
                self,
                'تحذير - Warning',
                'الرجاء اختيار مخزن\nPlease select a warehouse'
            )
            return
        
        # Get selected values
        self.selected_company_id = self.company_combo.currentData()
        self.selected_warehouse_id = self.warehouse_combo.currentData()
        
        # TODO: Save as default if checkbox is checked
        if self.save_default_checkbox.isChecked():
            logger.info(f'حفظ الاختيار الافتراضي: Company={self.selected_company_id}, '
                       f'Warehouse={self.selected_warehouse_id}')
        
        # Emit signal
        self.selection_confirmed.emit(
            self.selected_company_id,
            self.selected_warehouse_id
        )
        
        # Accept dialog
        self.accept()
    
    def get_selections(self):
        """Get selected company and warehouse IDs"""
        return self.selected_company_id, self.selected_warehouse_id
