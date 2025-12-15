"""
Main application entry point
نقطة الدخول الرئيسية للتطبيق
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from config import APP_CONFIG
from utils.logging import setup_logging, get_logger
from ui.styles.rtl_support import setup_rtl, load_theme
from ui.login_dialog import LoginDialog
from ui.company_selector import CompanySelectorDialog
from ui.main_window import MainWindow


logger = get_logger('main')


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger.info('بدء تشغيل نظام إدارة المخزون...')
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(APP_CONFIG['name'])
    app.setApplicationVersion(APP_CONFIG['version'])
    
    # Setup RTL support
    setup_rtl(app)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load and apply stylesheet (dark theme by default)
    stylesheet = load_theme('dark')
    app.setStyleSheet(stylesheet)
    
    # Show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() != LoginDialog.Accepted:
        logger.info('تم إلغاء تسجيل الدخول')
        return 0
    
    user = login_dialog.user
    logger.info(f'تسجيل دخول ناجح: {user.username}')
    
    # Show company/warehouse selector
    selector_dialog = CompanySelectorDialog(user)
    if selector_dialog.exec() != CompanySelectorDialog.Accepted:
        logger.info('تم إلغاء اختيار الشركة والمخزن')
        return 0
    
    company_id, warehouse_id = selector_dialog.get_selections()
    logger.info(f'تم اختيار الشركة: {company_id}, المخزن: {warehouse_id}')
    
    # Create and show main window
    main_window = MainWindow(user, company_id, warehouse_id)
    main_window.show()
    
    logger.info('تم بدء تشغيل النافذة الرئيسية')
    
    # Run application event loop
    return_code = app.exec()
    
    logger.info('تم إيقاف التطبيق')
    return return_code


if __name__ == '__main__':
    sys.exit(main())
