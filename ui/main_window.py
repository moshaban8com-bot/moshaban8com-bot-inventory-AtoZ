"""
Main Window - النافذة الرئيسية للنظام
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMenuBar, QMenu, QToolBar, QStatusBar, QTabWidget, QMessageBox,
    QDockWidget, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from datetime import datetime

from utils.logging import get_logger
from ui.dashboard import DashboardWidget
from ui.company_selector import CompanySelectorDialog

logger = get_logger('main_window')


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    company_changed = Signal(int)
    warehouse_changed = Signal(int)
    
    def __init__(self, user, company_id, warehouse_id):
        super().__init__()
        
        self.user = user
        self.current_company_id = company_id
        self.current_warehouse_id = warehouse_id
        
        self.setup_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_sidebar()
        self.create_status_bar()
        
        # Load dashboard as default
        self.load_dashboard()
        
        # Window settings
        self.setWindowTitle('نظام إدارة المخزون - Inventory Management System')
        self.resize(1400, 900)
        self.showMaximized()
        
    def setup_ui(self):
        """Setup main UI components"""
        # Central widget with tab interface
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        self.setCentralWidget(self.tab_widget)
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File Menu - ملف
        file_menu = menubar.addMenu('ملف / File')
        
        switch_company_action = QAction('تبديل شركة / Switch Company', self)
        switch_company_action.triggered.connect(self.switch_company)
        file_menu.addAction(switch_company_action)
        
        switch_warehouse_action = QAction('تبديل مخزن / Switch Warehouse', self)
        switch_warehouse_action.triggered.connect(self.switch_warehouse)
        file_menu.addAction(switch_warehouse_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('خروج / Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Masters Menu - البيانات الأساسية
        masters_menu = menubar.addMenu('البيانات الأساسية / Masters')
        
        items_action = QAction('الأصناف / Items', self)
        items_action.triggered.connect(lambda: self.open_screen('items'))
        masters_menu.addAction(items_action)
        
        categories_action = QAction('التصنيفات / Categories', self)
        categories_action.triggered.connect(lambda: self.open_screen('categories'))
        masters_menu.addAction(categories_action)
        
        warehouses_action = QAction('المخازن / Warehouses', self)
        warehouses_action.triggered.connect(lambda: self.open_screen('warehouses'))
        masters_menu.addAction(warehouses_action)
        
        locations_action = QAction('المواقع / Locations', self)
        locations_action.triggered.connect(lambda: self.open_screen('locations'))
        masters_menu.addAction(locations_action)
        
        masters_menu.addSeparator()
        
        uom_action = QAction('وحدات القياس / UOM', self)
        uom_action.triggered.connect(lambda: self.open_screen('uom'))
        masters_menu.addAction(uom_action)
        
        masters_menu.addSeparator()
        
        suppliers_action = QAction('الموردون / Suppliers', self)
        suppliers_action.triggered.connect(lambda: self.open_screen('suppliers'))
        masters_menu.addAction(suppliers_action)
        
        customers_action = QAction('العملاء / Customers', self)
        customers_action.triggered.connect(lambda: self.open_screen('customers'))
        masters_menu.addAction(customers_action)
        
        # Documents Menu - المستندات
        docs_menu = menubar.addMenu('المستندات / Documents')
        
        grn_action = QAction('استلام بضاعة / GRN Receipt', self)
        grn_action.setShortcut(QKeySequence('Ctrl+G'))
        grn_action.triggered.connect(lambda: self.open_screen('grn'))
        docs_menu.addAction(grn_action)
        
        issue_action = QAction('صرف بضاعة / Issue', self)
        issue_action.setShortcut(QKeySequence('Ctrl+I'))
        issue_action.triggered.connect(lambda: self.open_screen('issue'))
        docs_menu.addAction(issue_action)
        
        transfer_action = QAction('تحويل / Transfer', self)
        transfer_action.setShortcut(QKeySequence('Ctrl+T'))
        transfer_action.triggered.connect(lambda: self.open_screen('transfer'))
        docs_menu.addAction(transfer_action)
        
        adjustment_action = QAction('تسوية / Adjustment', self)
        adjustment_action.triggered.connect(lambda: self.open_screen('adjustment'))
        docs_menu.addAction(adjustment_action)
        
        stock_count_action = QAction('جرد مخزون / Stock Count', self)
        stock_count_action.triggered.connect(lambda: self.open_screen('stock_count'))
        docs_menu.addAction(stock_count_action)
        
        docs_menu.addSeparator()
        
        doc_list_action = QAction('قائمة المستندات / Document List', self)
        doc_list_action.triggered.connect(lambda: self.open_screen('doc_list'))
        docs_menu.addAction(doc_list_action)
        
        # Manufacturing Menu - التصنيع
        mfg_menu = menubar.addMenu('التصنيع / Manufacturing')
        
        bom_action = QAction('قائمة المواد / BOM', self)
        bom_action.triggered.connect(lambda: self.open_screen('bom'))
        mfg_menu.addAction(bom_action)
        
        prod_order_action = QAction('أوامر الإنتاج / Production Orders', self)
        prod_order_action.triggered.connect(lambda: self.open_screen('prod_order'))
        mfg_menu.addAction(prod_order_action)
        
        # Reports Menu - التقارير
        reports_menu = menubar.addMenu('التقارير / Reports')
        
        reports_center_action = QAction('مركز التقارير / Reports Center', self)
        reports_center_action.setShortcut(QKeySequence('Ctrl+R'))
        reports_center_action.triggered.connect(lambda: self.open_screen('reports'))
        reports_menu.addAction(reports_center_action)
        
        # Settings Menu - الإعدادات
        settings_menu = menubar.addMenu('الإعدادات / Settings')
        
        users_action = QAction('المستخدمون / Users', self)
        users_action.triggered.connect(lambda: self.open_screen('users'))
        settings_menu.addAction(users_action)
        
        roles_action = QAction('الأدوار والصلاحيات / Roles & Permissions', self)
        roles_action.triggered.connect(lambda: self.open_screen('roles'))
        settings_menu.addAction(roles_action)
        
        policies_action = QAction('السياسات / Policies', self)
        policies_action.triggered.connect(lambda: self.open_screen('policies'))
        settings_menu.addAction(policies_action)
        
        # Help Menu - مساعدة
        help_menu = menubar.addMenu('مساعدة / Help')
        
        about_action = QAction('حول / About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar('Main Toolbar')
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Quick access buttons
        new_doc_action = QAction('مستند جديد / New', self)
        new_doc_action.setShortcut(QKeySequence.New)
        new_doc_action.triggered.connect(self.new_document)
        toolbar.addAction(new_doc_action)
        
        refresh_action = QAction('تحديث / Refresh', self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_current)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # TODO: Add search widget to toolbar
        
    def create_sidebar(self):
        """Create collapsible sidebar"""
        sidebar = QDockWidget('التنقل / Navigation', self)
        sidebar.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        
        # Navigation list
        nav_list = QListWidget()
        nav_items = [
            ('لوحة التحكم / Dashboard', 'dashboard'),
            ('الأصناف / Items', 'items'),
            ('المستندات / Documents', 'doc_list'),
            ('التقارير / Reports', 'reports'),
        ]
        
        for text, screen_id in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, screen_id)
            nav_list.addItem(item)
        
        nav_list.itemClicked.connect(self.on_nav_item_clicked)
        sidebar.setWidget(nav_list)
        
        self.addDockWidget(Qt.RightDockWidgetArea, sidebar)
        
    def create_status_bar(self):
        """Create status bar"""
        status = QStatusBar()
        self.setStatusBar(status)
        
        # User info
        user_label = QLabel(f'المستخدم: {self.user.full_name_ar}')
        status.addPermanentWidget(user_label)
        
        # Company info
        self.company_label = QLabel(f'الشركة: {self.current_company_id}')
        status.addPermanentWidget(self.company_label)
        
        # Warehouse info
        self.warehouse_label = QLabel(f'المخزن: {self.current_warehouse_id}')
        status.addPermanentWidget(self.warehouse_label)
        
        # Date/Time
        datetime_label = QLabel(datetime.now().strftime('%Y-%m-%d %H:%M'))
        status.addPermanentWidget(datetime_label)
        
    def load_dashboard(self):
        """Load dashboard widget"""
        dashboard = DashboardWidget(
            self.current_company_id,
            self.current_warehouse_id
        )
        self.add_tab(dashboard, 'لوحة التحكم / Dashboard')
        
    def add_tab(self, widget, title):
        """Add a new tab to the tab widget"""
        index = self.tab_widget.addTab(widget, title)
        self.tab_widget.setCurrentIndex(index)
        
    def close_tab(self, index):
        """Close a tab"""
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget.deleteLater()
        
    def open_screen(self, screen_id):
        """Open a screen in a new tab"""
        logger.info(f'فتح شاشة: {screen_id}')
        
        # Check if screen is already open
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'screen_id') and widget.screen_id == screen_id:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # Create screen widget based on screen_id
        widget = None
        title = screen_id
        
        try:
            if screen_id == 'items':
                from ui.masters.items_screen import ItemsScreen
                widget = ItemsScreen(self.current_company_id, self)
                title = 'الأصناف / Items'
            # TODO: Add other screens
            else:
                # Placeholder for unimplemented screens
                placeholder = QWidget()
                layout = QVBoxLayout(placeholder)
                label = QLabel(f'قيد التطوير - Under Development\n\nScreen: {screen_id}')
                label.setAlignment(Qt.AlignCenter)
                layout.addWidget(label)
                widget = placeholder
                title = f'{screen_id}'
            
            if widget:
                widget.screen_id = screen_id
                self.add_tab(widget, title)
                
        except Exception as e:
            logger.error(f'Error opening screen {screen_id}: {str(e)}', exc_info=True)
            QMessageBox.critical(
                self,
                'خطأ / Error',
                f'خطأ في فتح الشاشة\nError opening screen:\n{str(e)}'
            )
        
    def on_nav_item_clicked(self, item):
        """Handle navigation item click"""
        screen_id = item.data(Qt.UserRole)
        if screen_id == 'dashboard':
            self.load_dashboard()
        else:
            self.open_screen(screen_id)
        
    def switch_company(self):
        """Switch to different company"""
        dialog = CompanySelectorDialog(self.user, self)
        if dialog.exec():
            company_id, warehouse_id = dialog.get_selections()
            self.current_company_id = company_id
            self.current_warehouse_id = warehouse_id
            self.company_changed.emit(company_id)
            self.warehouse_changed.emit(warehouse_id)
            logger.info(f'تبديل الشركة: {company_id}, المخزن: {warehouse_id}')
            
    def switch_warehouse(self):
        """Switch to different warehouse"""
        # TODO: Implement warehouse-only selector
        self.switch_company()
        
    def new_document(self):
        """Create new document"""
        # TODO: Show document type selector
        logger.info('مستند جديد')
        
    def refresh_current(self):
        """Refresh current tab"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'refresh'):
            current_widget.refresh()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            'حول النظام / About',
            'نظام إدارة المخزون\n'
            'Inventory Management System\n\n'
            'الإصدار 1.0.0\n'
            'Version 1.0.0\n\n'
            '© 2024 All Rights Reserved'
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            'تأكيد الخروج / Confirm Exit',
            'هل تريد حقاً الخروج من النظام؟\nDo you really want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info('إغلاق النافذة الرئيسية')
            event.accept()
        else:
            event.ignore()
