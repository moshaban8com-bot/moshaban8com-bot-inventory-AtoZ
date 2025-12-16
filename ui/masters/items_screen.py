"""
Items Screen - شاشة الأصناف
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QMessageBox,
    QGroupBox, QCheckBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt

from data import session_scope, Item, ItemCategory, UOM
from ui.widgets import DataTableWidget, SearchBoxWidget, ComboSearchWidget, show_success, show_error
from utils.logging import get_logger

logger = get_logger('items_screen')


class ItemsScreen(QWidget):
    """Items master data screen"""
    
    def __init__(self, company_id, parent=None):
        super().__init__(parent)
        
        self.company_id = company_id
        self.current_filter = ''
        
        self.setup_ui()
        self.load_items()
        
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('الأصناف / Items')
        title.setProperty('heading', True)
        layout.addWidget(title)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Search box
        self.search_box = SearchBoxWidget('بحث في الأصناف... / Search items...')
        self.search_box.search_triggered.connect(self.on_search)
        self.search_box.search_cleared.connect(self.load_items)
        toolbar_layout.addWidget(self.search_box)
        
        toolbar_layout.addStretch()
        
        # Buttons
        self.new_button = QPushButton('جديد / New')
        self.new_button.setProperty('success', True)
        self.new_button.clicked.connect(self.new_item)
        toolbar_layout.addWidget(self.new_button)
        
        self.edit_button = QPushButton('تعديل / Edit')
        self.edit_button.clicked.connect(self.edit_item)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton('حذف / Delete')
        self.delete_button.setProperty('danger', True)
        self.delete_button.clicked.connect(self.delete_item)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton('تحديث / Refresh')
        self.refresh_button.setProperty('secondary', True)
        self.refresh_button.clicked.connect(self.load_items)
        toolbar_layout.addWidget(self.refresh_button)
        
        layout.addLayout(toolbar_layout)
        
        # Table
        self.table = DataTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'الكود / Code',
            'الاسم عربي / Name AR',
            'الاسم إنجليزي / Name EN',
            'التصنيف / Category',
            'وحدة القياس / UOM',
            'النوع / Type',
            'نشط / Active'
        ])
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(lambda: self.edit_item())
        layout.addWidget(self.table)
        
    def load_items(self):
        """Load items from database"""
        try:
            with session_scope() as session:
                query = session.query(Item).filter_by(company_id=self.company_id)
                
                # Apply search filter if exists
                if self.current_filter:
                    query = query.filter(
                        (Item.code.like(f'%{self.current_filter}%')) |
                        (Item.name_ar.like(f'%{self.current_filter}%')) |
                        (Item.name_en.like(f'%{self.current_filter}%'))
                    )
                
                items = query.all()
                
                self.table.setRowCount(len(items))
                
                for row, item in enumerate(items):
                    self.table.setItem(row, 0, self._create_table_item(item.code))
                    self.table.setItem(row, 1, self._create_table_item(item.name_ar))
                    self.table.setItem(row, 2, self._create_table_item(item.name_en))
                    
                    category_name = item.category.name_ar if item.category else ''
                    self.table.setItem(row, 3, self._create_table_item(category_name))
                    
                    uom_name = item.base_uom.name_ar if item.base_uom else ''
                    self.table.setItem(row, 4, self._create_table_item(uom_name))
                    
                    self.table.setItem(row, 5, self._create_table_item(item.item_type.value))
                    self.table.setItem(row, 6, self._create_table_item('نعم' if item.is_active else 'لا'))
                    
                    # Store item ID in first column
                    self.table.item(row, 0).setData(Qt.UserRole, item.id)
                
                logger.info(f'Loaded {len(items)} items')
                
        except Exception as e:
            logger.error(f'Error loading items: {str(e)}', exc_info=True)
            show_error(self, f'خطأ في تحميل الأصناف\nError loading items:\n{str(e)}')
            
    def _create_table_item(self, text):
        """Create a table item"""
        from PySide6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
        return item
        
    def on_search(self, search_text):
        """Handle search"""
        self.current_filter = search_text
        self.load_items()
        
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def new_item(self):
        """Create new item"""
        dialog = ItemDialog(self.company_id, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_items()
            show_success(self, 'تم إضافة الصنف بنجاح / Item added successfully')
            
    def edit_item(self):
        """Edit selected item"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        item_id = self.table.item(current_row, 0).data(Qt.UserRole)
        
        dialog = ItemDialog(self.company_id, self, item_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_items()
            show_success(self, 'تم تعديل الصنف بنجاح / Item updated successfully')
            
    def delete_item(self):
        """Delete selected item"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        item_code = self.table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self,
            'تأكيد الحذف / Confirm Delete',
            f'هل تريد حقاً حذف الصنف "{item_code}"؟\n'
            f'Do you really want to delete item "{item_code}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                item_id = self.table.item(current_row, 0).data(Qt.UserRole)
                
                with session_scope() as session:
                    item = session.query(Item).get(item_id)
                    if item:
                        session.delete(item)
                        session.commit()
                        
                self.load_items()
                show_success(self, 'تم حذف الصنف بنجاح / Item deleted successfully')
                
            except Exception as e:
                logger.error(f'Error deleting item: {str(e)}', exc_info=True)
                show_error(self, f'خطأ في حذف الصنف\nError deleting item:\n{str(e)}')
                
    def refresh(self):
        """Refresh data"""
        self.load_items()


class ItemDialog(QDialog):
    """Dialog for adding/editing items"""
    
    def __init__(self, company_id, parent=None, item_id=None):
        super().__init__(parent)
        
        self.company_id = company_id
        self.item_id = item_id
        self.item = None
        
        self.setup_ui()
        self.load_lookups()
        
        if item_id:
            self.load_item()
            self.setWindowTitle('تعديل صنف / Edit Item')
        else:
            self.setWindowTitle('صنف جديد / New Item')
            
        self.resize(600, 500)
        
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Code
        self.code_edit = QLineEdit()
        form_layout.addRow('الكود / Code *', self.code_edit)
        
        # Name AR
        self.name_ar_edit = QLineEdit()
        form_layout.addRow('الاسم عربي / Name AR *', self.name_ar_edit)
        
        # Name EN
        self.name_en_edit = QLineEdit()
        form_layout.addRow('الاسم إنجليزي / Name EN *', self.name_en_edit)
        
        # Description AR
        self.desc_ar_edit = QTextEdit()
        self.desc_ar_edit.setMaximumHeight(80)
        form_layout.addRow('الوصف عربي / Description AR', self.desc_ar_edit)
        
        # Category
        self.category_combo = ComboSearchWidget()
        form_layout.addRow('التصنيف / Category', self.category_combo)
        
        # UOM
        self.uom_combo = ComboSearchWidget()
        form_layout.addRow('وحدة القياس / UOM *', self.uom_combo)
        
        # Reorder Point
        self.reorder_spin = QDoubleSpinBox()
        self.reorder_spin.setRange(0, 999999)
        self.reorder_spin.setDecimals(2)
        form_layout.addRow('حد الطلب / Reorder Point', self.reorder_spin)
        
        # Active
        self.active_check = QCheckBox('نشط / Active')
        self.active_check.setChecked(True)
        form_layout.addRow('', self.active_check)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton('إلغاء / Cancel')
        self.cancel_button.setProperty('secondary', True)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton('حفظ / Save')
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.save_item)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
    def load_lookups(self):
        """Load lookup data"""
        try:
            with session_scope() as session:
                # Load categories
                categories = session.query(ItemCategory).filter_by(
                    company_id=self.company_id,
                    is_active=True
                ).all()
                
                for category in categories:
                    self.category_combo.add_item(
                        f'{category.name_ar} - {category.name_en}',
                        category.id
                    )
                
                # Load UOMs
                uoms = session.query(UOM).filter_by(is_active=True).all()
                
                for uom in uoms:
                    self.uom_combo.add_item(
                        f'{uom.name_ar} - {uom.name_en}',
                        uom.id
                    )
                    
        except Exception as e:
            logger.error(f'Error loading lookups: {str(e)}', exc_info=True)
            
    def load_item(self):
        """Load item data"""
        try:
            with session_scope() as session:
                self.item = session.query(Item).get(self.item_id)
                
                if self.item:
                    self.code_edit.setText(self.item.code)
                    self.name_ar_edit.setText(self.item.name_ar)
                    self.name_en_edit.setText(self.item.name_en)
                    self.desc_ar_edit.setPlainText(self.item.description_ar or '')
                    
                    if self.item.category_id:
                        self.category_combo.set_selected_by_data(self.item.category_id)
                    
                    if self.item.base_uom_id:
                        self.uom_combo.set_selected_by_data(self.item.base_uom_id)
                    
                    self.reorder_spin.setValue(float(self.item.reorder_point or 0))
                    self.active_check.setChecked(self.item.is_active)
                    
        except Exception as e:
            logger.error(f'Error loading item: {str(e)}', exc_info=True)
            
    def save_item(self):
        """Save item"""
        # Validate
        if not self.code_edit.text().strip():
            QMessageBox.warning(self, 'تحذير / Warning', 'الرجاء إدخال الكود / Please enter code')
            return
            
        if not self.name_ar_edit.text().strip():
            QMessageBox.warning(self, 'تحذير / Warning', 'الرجاء إدخال الاسم عربي / Please enter Arabic name')
            return
            
        if not self.uom_combo.get_selected_data():
            QMessageBox.warning(self, 'تحذير / Warning', 'الرجاء اختيار وحدة القياس / Please select UOM')
            return
        
        try:
            with session_scope() as session:
                if self.item_id:
                    # Update existing
                    item = session.query(Item).get(self.item_id)
                else:
                    # Create new
                    item = Item(company_id=self.company_id)
                    session.add(item)
                
                item.code = self.code_edit.text().strip()
                item.name_ar = self.name_ar_edit.text().strip()
                item.name_en = self.name_en_edit.text().strip()
                item.description_ar = self.desc_ar_edit.toPlainText().strip() or None
                item.category_id = self.category_combo.get_selected_data()
                item.base_uom_id = self.uom_combo.get_selected_data()
                item.reorder_point = self.reorder_spin.value()
                item.is_active = self.active_check.isChecked()
                
                session.commit()
                
            self.accept()
            
        except Exception as e:
            logger.error(f'Error saving item: {str(e)}', exc_info=True)
            QMessageBox.critical(
                self,
                'خطأ / Error',
                f'خطأ في حفظ الصنف\nError saving item:\n{str(e)}'
            )
