"""
Reports Center - مركز التقارير
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QSplitter, QGroupBox,
    QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt

from ui.widgets import DatePickerWidget, ComboSearchWidget
from utils.logging import get_logger

logger = get_logger('reports_center')


class ReportsCenterScreen(QWidget):
    """Reports center screen"""
    
    def __init__(self, company_id, warehouse_id, parent=None):
        super().__init__(parent)
        
        self.company_id = company_id
        self.warehouse_id = warehouse_id
        
        self.setup_ui()
        self.load_reports()
        
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('مركز التقارير / Reports Center')
        title.setProperty('heading', True)
        layout.addWidget(title)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Reports list
        reports_widget = self.create_reports_list()
        splitter.addWidget(reports_widget)
        
        # Right: Filters and preview
        filters_widget = self.create_filters_section()
        splitter.addWidget(filters_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
    def create_reports_list(self):
        """Create reports list"""
        group = QGroupBox('التقارير المتاحة / Available Reports')
        layout = QVBoxLayout(group)
        
        self.reports_list = QListWidget()
        self.reports_list.currentItemChanged.connect(self.on_report_selected)
        layout.addWidget(self.reports_list)
        
        return group
        
    def create_filters_section(self):
        """Create filters section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Report info
        self.report_info_label = QLabel('اختر تقريراً من القائمة / Select a report from the list')
        self.report_info_label.setAlignment(Qt.AlignCenter)
        self.report_info_label.setStyleSheet('color: #64748b; padding: 20px;')
        layout.addWidget(self.report_info_label)
        
        # Filters group
        self.filters_group = QGroupBox('فلاتر التقرير / Report Filters')
        self.filters_group.setVisible(False)
        filters_layout = QFormLayout(self.filters_group)
        
        # Date From
        self.date_from_picker = DatePickerWidget()
        filters_layout.addRow('من تاريخ / From Date:', self.date_from_picker)
        
        # Date To
        self.date_to_picker = DatePickerWidget()
        filters_layout.addRow('إلى تاريخ / To Date:', self.date_to_picker)
        
        # Warehouse
        self.warehouse_combo = ComboSearchWidget()
        self.warehouse_combo.add_item('الكل / All', None)
        filters_layout.addRow('المخزن / Warehouse:', self.warehouse_combo)
        
        # Category
        self.category_combo = ComboSearchWidget()
        self.category_combo.add_item('الكل / All', None)
        filters_layout.addRow('التصنيف / Category:', self.category_combo)
        
        layout.addWidget(self.filters_group)
        
        layout.addStretch()
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.preview_button = QPushButton('معاينة / Preview')
        self.preview_button.clicked.connect(self.preview_report)
        buttons_layout.addWidget(self.preview_button)
        
        self.export_excel_button = QPushButton('تصدير Excel / Export Excel')
        self.export_excel_button.setProperty('success', True)
        self.export_excel_button.clicked.connect(self.export_excel)
        buttons_layout.addWidget(self.export_excel_button)
        
        self.export_pdf_button = QPushButton('تصدير PDF / Export PDF')
        self.export_pdf_button.setProperty('secondary', True)
        self.export_pdf_button.clicked.connect(self.export_pdf)
        buttons_layout.addWidget(self.export_pdf_button)
        
        layout.addLayout(buttons_layout)
        
        return widget
        
    def load_reports(self):
        """Load available reports"""
        reports = [
            ('تقرير المخزون الحالي / Stock on Hand', 'stock_on_hand'),
            ('تقييم المخزون / Inventory Valuation', 'inventory_valuation'),
            ('كارت الصنف / Item Card', 'item_card'),
            ('ملخص الحركة / Movement Summary', 'movement_summary'),
            ('تقرير إعادة الطلب / Reorder Report', 'reorder_report'),
            ('تتبع الدفعات / Lot Traceability', 'lot_traceability'),
        ]
        
        for name, report_id in reports:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, report_id)
            self.reports_list.addItem(item)
            
    def on_report_selected(self, current, previous):
        """Handle report selection"""
        if current:
            report_id = current.data(Qt.UserRole)
            report_name = current.text()
            
            self.report_info_label.setText(f'التقرير المحدد: {report_name}\nSelected Report: {report_name}')
            self.filters_group.setVisible(True)
            
            logger.info(f'Selected report: {report_id}')
            
    def preview_report(self):
        """Preview report"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'الرجاء اختيار تقرير\nPlease select a report'
            )
            return
            
        report_id = current_item.data(Qt.UserRole)
        logger.info(f'Previewing report: {report_id}')
        
        QMessageBox.information(
            self,
            'معاينة التقرير / Report Preview',
            f'معاينة التقرير قيد التطوير\nReport preview under development\n\nReport: {report_id}'
        )
        
    def export_excel(self):
        """Export report to Excel"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'الرجاء اختيار تقرير\nPlease select a report'
            )
            return
            
        report_id = current_item.data(Qt.UserRole)
        logger.info(f'Exporting report to Excel: {report_id}')
        
        QMessageBox.information(
            self,
            'تصدير Excel / Export Excel',
            f'تصدير إلى Excel قيد التطوير\nExcel export under development\n\nReport: {report_id}'
        )
        
    def export_pdf(self):
        """Export report to PDF"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                'تحذير / Warning',
                'الرجاء اختيار تقرير\nPlease select a report'
            )
            return
            
        report_id = current_item.data(Qt.UserRole)
        logger.info(f'Exporting report to PDF: {report_id}')
        
        QMessageBox.information(
            self,
            'تصدير PDF / Export PDF',
            f'تصدير إلى PDF قيد التطوير\nPDF export under development\n\nReport: {report_id}'
        )
        
    def refresh(self):
        """Refresh reports"""
        pass
