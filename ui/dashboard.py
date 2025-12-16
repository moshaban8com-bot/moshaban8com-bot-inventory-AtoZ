"""
Dashboard Widget - لوحة التحكم الرئيسية
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from decimal import Decimal

from data import session_scope, Item
from utils.logging import get_logger

logger = get_logger('dashboard')


class DashboardWidget(QWidget):
    """Main dashboard widget with KPIs and charts"""
    
    def __init__(self, company_id, warehouse_id, parent=None):
        super().__init__(parent)
        
        self.company_id = company_id
        self.warehouse_id = warehouse_id
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('لوحة التحكم / Dashboard')
        title.setProperty('heading', True)
        layout.addWidget(title)
        
        # KPI Cards Row
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        # Total Inventory Value Card
        self.inventory_value_card = self.create_kpi_card(
            'قيمة المخزون الإجمالية',
            'Total Inventory Value',
            '0.00',
            '#2563eb'
        )
        kpi_layout.addWidget(self.inventory_value_card)
        
        # Total Items Card
        self.total_items_card = self.create_kpi_card(
            'عدد الأصناف',
            'Total Items',
            '0',
            '#22c55e'
        )
        kpi_layout.addWidget(self.total_items_card)
        
        # Today's Movements Card
        self.movements_card = self.create_kpi_card(
            'حركات اليوم',
            "Today's Movements",
            '0',
            '#f59e0b'
        )
        kpi_layout.addWidget(self.movements_card)
        
        # Items Below Reorder Card
        self.reorder_card = self.create_kpi_card(
            'أصناف تحت حد الطلب',
            'Items Below Reorder',
            '0',
            '#ef4444'
        )
        kpi_layout.addWidget(self.reorder_card)
        
        layout.addLayout(kpi_layout)
        
        # Charts placeholder
        charts_layout = QHBoxLayout()
        
        # Top Items Chart
        top_items_frame = QFrame()
        top_items_frame.setFrameShape(QFrame.StyledPanel)
        top_items_layout = QVBoxLayout(top_items_frame)
        
        top_items_title = QLabel('أكثر 10 أصناف حركة / Top 10 Moving Items')
        top_items_title.setStyleSheet('font-weight: bold; font-size: 12pt;')
        top_items_layout.addWidget(top_items_title)
        
        top_items_placeholder = QLabel('الرسم البياني قيد التطوير\nChart Under Development')
        top_items_placeholder.setAlignment(Qt.AlignCenter)
        top_items_placeholder.setStyleSheet('color: #64748b; padding: 40px;')
        top_items_layout.addWidget(top_items_placeholder)
        
        charts_layout.addWidget(top_items_frame)
        
        # Warehouse Distribution Chart
        warehouse_dist_frame = QFrame()
        warehouse_dist_frame.setFrameShape(QFrame.StyledPanel)
        warehouse_dist_layout = QVBoxLayout(warehouse_dist_frame)
        
        warehouse_dist_title = QLabel('توزيع المخزون / Stock Distribution')
        warehouse_dist_title.setStyleSheet('font-weight: bold; font-size: 12pt;')
        warehouse_dist_layout.addWidget(warehouse_dist_title)
        
        warehouse_dist_placeholder = QLabel('الرسم البياني قيد التطوير\nChart Under Development')
        warehouse_dist_placeholder.setAlignment(Qt.AlignCenter)
        warehouse_dist_placeholder.setStyleSheet('color: #64748b; padding: 40px;')
        warehouse_dist_layout.addWidget(warehouse_dist_placeholder)
        
        charts_layout.addWidget(warehouse_dist_frame)
        
        layout.addLayout(charts_layout)
        
        # Quick Actions
        actions_label = QLabel('إجراءات سريعة / Quick Actions')
        actions_label.setStyleSheet('font-weight: bold; font-size: 12pt; margin-top: 10px;')
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        
        new_grn_btn = QPushButton('استلام بضاعة جديد / New GRN')
        new_grn_btn.setProperty('success', True)
        actions_layout.addWidget(new_grn_btn)
        
        new_issue_btn = QPushButton('صرف بضاعة جديد / New Issue')
        actions_layout.addWidget(new_issue_btn)
        
        new_transfer_btn = QPushButton('تحويل جديد / New Transfer')
        actions_layout.addWidget(new_transfer_btn)
        
        stock_report_btn = QPushButton('تقرير المخزون / Stock Report')
        stock_report_btn.setProperty('secondary', True)
        actions_layout.addWidget(stock_report_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
    def create_kpi_card(self, title_ar, title_en, value, color):
        """Create a KPI card widget"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Title
        title = QLabel(f'{title_ar}\n{title_en}')
        title.setStyleSheet('color: #64748b; font-size: 10pt;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f'color: {color}; font-size: 24pt; font-weight: bold;')
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Store value label for updates
        frame.value_label = value_label
        
        return frame
        
    def load_data(self):
        """Load dashboard data"""
        try:
            with session_scope() as session:
                # Count total items
                total_items = session.query(Item).filter_by(
                    company_id=self.company_id,
                    is_active=True
                ).count()
                
                self.total_items_card.value_label.setText(str(total_items))
                
                # TODO: Calculate other KPIs from stock ledger
                # - Total inventory value
                # - Today's movements
                # - Items below reorder point
                
                logger.info(f'Dashboard data loaded: {total_items} items')
                
        except Exception as e:
            logger.error(f'Error loading dashboard data: {str(e)}', exc_info=True)
            
    def refresh(self):
        """Refresh dashboard data"""
        self.load_data()
