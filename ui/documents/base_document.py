"""
Base Document Screen - الشاشة الأساسية للمستندات
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QGroupBox, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime
from decimal import Decimal

from data.models import DocumentStatus
from ui.widgets import DataTableWidget, DatePickerWidget, ComboSearchWidget, show_success, show_error
from utils.logging import get_logger

logger = get_logger('base_document')


class BaseDocumentScreen(QWidget):
    """Base class for all document entry screens"""
    
    # Signals
    document_saved = Signal(int)  # Emits document ID
    document_posted = Signal(int)
    document_cancelled = Signal(int)
    
    def __init__(self, company_id, warehouse_id, document_type, parent=None):
        super().__init__(parent)
        
        self.company_id = company_id
        self.warehouse_id = warehouse_id
        self.document_type = document_type
        self.document_id = None
        self.current_status = DocumentStatus.DRAFT
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setProperty('heading', True)
        layout.addWidget(self.title_label)
        
        # Status indicator
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.status_label)
        self.update_status_label()
        
        # Splitter for header and lines
        splitter = QSplitter(Qt.Vertical)
        
        # Header section
        header_widget = self.create_header_section()
        splitter.addWidget(header_widget)
        
        # Lines section
        lines_widget = self.create_lines_section()
        splitter.addWidget(lines_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        # Totals section
        totals_widget = self.create_totals_section()
        layout.addWidget(totals_widget)
        
        # Action buttons
        buttons_layout = self.create_action_buttons()
        layout.addLayout(buttons_layout)
        
    def create_header_section(self):
        """Create document header section - to be overridden"""
        group = QGroupBox('معلومات المستند / Document Header')
        layout = QFormLayout(group)
        
        # Document Number
        self.doc_number_label = QLabel('سيتم إنشاؤه تلقائياً / Auto-generated')
        layout.addRow('رقم المستند / Doc Number:', self.doc_number_label)
        
        # Date
        self.date_picker = DatePickerWidget()
        layout.addRow('التاريخ / Date:', self.date_picker)
        
        # Notes
        from PySide6.QtWidgets import QTextEdit
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        layout.addRow('ملاحظات / Notes:', self.notes_edit)
        
        return group
        
    def create_lines_section(self):
        """Create document lines section"""
        group = QGroupBox('الأصناف / Items')
        layout = QVBoxLayout(group)
        
        # Toolbar for lines
        toolbar = QHBoxLayout()
        
        self.add_line_button = QPushButton('إضافة صنف / Add Item')
        self.add_line_button.setProperty('success', True)
        self.add_line_button.clicked.connect(self.add_line)
        toolbar.addWidget(self.add_line_button)
        
        self.remove_line_button = QPushButton('حذف الصف / Remove Line')
        self.remove_line_button.setProperty('danger', True)
        self.remove_line_button.clicked.connect(self.remove_line)
        toolbar.addWidget(self.remove_line_button)
        
        toolbar.addStretch()
        
        paste_info = QLabel('يمكنك اللصق من Excel باستخدام Ctrl+V / Paste from Excel with Ctrl+V')
        paste_info.setStyleSheet('color: #64748b; font-size: 9pt;')
        toolbar.addWidget(paste_info)
        
        layout.addLayout(toolbar)
        
        # Lines table
        self.lines_table = DataTableWidget()
        self.lines_table.setColumnCount(5)
        self.lines_table.setHorizontalHeaderLabels([
            'الصنف / Item',
            'الوصف / Description',
            'الكمية / Quantity',
            'السعر / Price',
            'الإجمالي / Total'
        ])
        self.lines_table.data_changed.connect(self.calculate_totals)
        layout.addWidget(self.lines_table)
        
        return group
        
    def create_totals_section(self):
        """Create totals section"""
        group = QGroupBox('الإجماليات / Totals')
        layout = QHBoxLayout(group)
        layout.setSpacing(20)
        
        layout.addStretch()
        
        # Total Quantity
        qty_layout = QVBoxLayout()
        qty_label = QLabel('إجمالي الكمية / Total Qty:')
        qty_label.setStyleSheet('font-weight: bold;')
        qty_layout.addWidget(qty_label)
        
        self.total_qty_label = QLabel('0.00')
        self.total_qty_label.setStyleSheet('font-size: 14pt; color: #2563eb;')
        self.total_qty_label.setAlignment(Qt.AlignRight)
        qty_layout.addWidget(self.total_qty_label)
        
        layout.addLayout(qty_layout)
        
        # Total Amount
        amount_layout = QVBoxLayout()
        amount_label = QLabel('إجمالي القيمة / Total Amount:')
        amount_label.setStyleSheet('font-weight: bold;')
        amount_layout.addWidget(amount_label)
        
        self.total_amount_label = QLabel('0.00')
        self.total_amount_label.setStyleSheet('font-size: 14pt; color: #22c55e;')
        self.total_amount_label.setAlignment(Qt.AlignRight)
        amount_layout.addWidget(self.total_amount_label)
        
        layout.addLayout(amount_layout)
        
        return group
        
    def create_action_buttons(self):
        """Create action buttons"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # Save as Draft
        self.save_button = QPushButton('حفظ كمسودة / Save as Draft')
        self.save_button.clicked.connect(self.save_document)
        layout.addWidget(self.save_button)
        
        # Post
        self.post_button = QPushButton('ترحيل / Post')
        self.post_button.setProperty('success', True)
        self.post_button.clicked.connect(self.post_document)
        self.post_button.setShortcut('F9')
        layout.addWidget(self.post_button)
        
        # Cancel
        self.cancel_button = QPushButton('إلغاء / Cancel')
        self.cancel_button.setProperty('danger', True)
        self.cancel_button.clicked.connect(self.cancel_document)
        layout.addWidget(self.cancel_button)
        
        return layout
        
    def update_status_label(self):
        """Update status label"""
        status_text = {
            DocumentStatus.DRAFT: ('مسودة / Draft', 'draft'),
            DocumentStatus.SUBMITTED: ('مقدم / Submitted', 'submitted'),
            DocumentStatus.APPROVED: ('معتمد / Approved', 'approved'),
            DocumentStatus.POSTED: ('مرحل / Posted', 'posted'),
            DocumentStatus.CANCELLED: ('ملغي / Cancelled', 'cancelled'),
        }
        
        text, attr = status_text.get(self.current_status, ('', ''))
        self.status_label.setText(f'الحالة / Status: {text}')
        self.status_label.setProperty('status', attr)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
        # Update button states based on status
        is_draft = self.current_status == DocumentStatus.DRAFT
        is_posted = self.current_status == DocumentStatus.POSTED
        
        self.save_button.setEnabled(is_draft)
        self.post_button.setEnabled(is_draft)
        self.add_line_button.setEnabled(is_draft)
        self.remove_line_button.setEnabled(is_draft)
        self.lines_table.setEnabled(is_draft)
        
    def add_line(self):
        """Add a new line to the document"""
        current_row = self.lines_table.rowCount()
        self.lines_table.insertRow(current_row)
        
    def remove_line(self):
        """Remove selected line"""
        current_row = self.lines_table.currentRow()
        if current_row >= 0:
            self.lines_table.removeRow(current_row)
            self.calculate_totals()
            
    def calculate_totals(self):
        """Calculate and update totals"""
        total_qty = Decimal('0')
        total_amount = Decimal('0')
        
        for row in range(self.lines_table.rowCount()):
            # Get quantity
            qty_item = self.lines_table.item(row, 2)
            qty = Decimal(qty_item.text() if qty_item and qty_item.text() else '0')
            
            # Get price
            price_item = self.lines_table.item(row, 3)
            price = Decimal(price_item.text() if price_item and price_item.text() else '0')
            
            # Calculate line total
            line_total = qty * price
            
            # Update total column
            total_item = self.lines_table.item(row, 4)
            if not total_item:
                from PySide6.QtWidgets import QTableWidgetItem
                total_item = QTableWidgetItem()
                self.lines_table.setItem(row, 4, total_item)
            total_item.setText(f'{line_total:.2f}')
            
            total_qty += qty
            total_amount += line_total
            
        self.total_qty_label.setText(f'{total_qty:.2f}')
        self.total_amount_label.setText(f'{total_amount:.2f}')
        
    def save_document(self):
        """Save document as draft - to be overridden"""
        logger.info('Saving document...')
        show_success(self, 'تم حفظ المستند كمسودة / Document saved as draft')
        
    def post_document(self):
        """Post document - to be overridden"""
        reply = QMessageBox.question(
            self,
            'تأكيد الترحيل / Confirm Posting',
            'هل تريد ترحيل المستند؟ لن يمكنك التعديل بعد الترحيل.\n'
            'Do you want to post the document? You cannot edit after posting.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info('Posting document...')
            self.current_status = DocumentStatus.POSTED
            self.update_status_label()
            show_success(self, 'تم ترحيل المستند بنجاح / Document posted successfully')
            
    def cancel_document(self):
        """Cancel document"""
        if self.current_status == DocumentStatus.POSTED:
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'لا يمكن إلغاء مستند مرحل\nCannot cancel posted document'
            )
            return
            
        reply = QMessageBox.question(
            self,
            'تأكيد الإلغاء / Confirm Cancel',
            'هل تريد إلغاء المستند؟\nDo you want to cancel the document?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_status = DocumentStatus.CANCELLED
            self.update_status_label()
            show_success(self, 'تم إلغاء المستند / Document cancelled')
            
    def refresh(self):
        """Refresh document data"""
        pass
