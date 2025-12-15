"""
Main application entry point
نقطة الدخول الرئيسية للتطبيق
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from config import APP_CONFIG
from utils.logging import setup_logging, get_logger


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
    
    # Set RTL layout if configured
    if APP_CONFIG['rtl']:
        app.setLayoutDirection(Qt.RightToLeft)
    
    # Set application style
    app.setStyle('Fusion')
    
    # TODO: Load and apply stylesheet
    # TODO: Create and show login window
    
    # Show temporary message
    msg = QMessageBox()
    msg.setWindowTitle(APP_CONFIG['name'])
    msg.setText('مرحباً بكم في نظام إدارة المخزون\n\n'
                'Welcome to Inventory Management System\n\n'
                'النظام قيد التطوير - System Under Development')
    msg.setInformativeText(
        'لإنشاء البيانات التجريبية، قم بتشغيل:\n'
        'To create demo data, run:\n\n'
        'python -m data.seed'
    )
    msg.setIcon(QMessageBox.Information)
    msg.exec()
    
    logger.info('تم إيقاف التطبيق')
    return 0


if __name__ == '__main__':
    sys.exit(main())
