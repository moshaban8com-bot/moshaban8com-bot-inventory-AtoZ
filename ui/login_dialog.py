"""
Login Dialog - شاشة تسجيل الدخول
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon

from security.auth import AuthService, AuthenticationError
from utils.logging import get_logger

logger = get_logger('login')


class LoginDialog(QDialog):
    """Login dialog for user authentication"""
    
    # Signals
    login_successful = Signal(object)  # Emits user object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.company = None
        self.warehouse = None
        self.auth_service = AuthService()
        
        self.setup_ui()
        self.setWindowTitle('تسجيل الدخول - Login')
        self.setModal(True)
        self.setFixedSize(400, 500)
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Title Section
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel('نظام إدارة المخزون')
        title_label.setProperty('heading', True)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel('Inventory Management System')
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet('color: #64748b; font-size: 10pt;')
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addSpacing(20)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        layout.addSpacing(10)
        
        # Username field
        username_label = QLabel('اسم المستخدم / Username')
        layout.addWidget(username_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('أدخل اسم المستخدم')
        self.username_edit.returnPressed.connect(self.on_login)
        layout.addWidget(self.username_edit)
        
        layout.addSpacing(10)
        
        # Password field
        password_label = QLabel('كلمة المرور / Password')
        layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('أدخل كلمة المرور')
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.returnPressed.connect(self.on_login)
        layout.addWidget(self.password_edit)
        
        layout.addSpacing(10)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox('تذكرني / Remember Me')
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(20)
        
        # Login button
        self.login_button = QPushButton('تسجيل الدخول / Login')
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.on_login)
        layout.addWidget(self.login_button)
        
        # Forgot password button
        self.forgot_button = QPushButton('نسيت كلمة المرور؟ / Forgot Password?')
        self.forgot_button.setProperty('secondary', True)
        self.forgot_button.clicked.connect(self.on_forgot_password)
        layout.addWidget(self.forgot_button)
        
        layout.addStretch()
        
        # Version label
        version_label = QLabel('الإصدار 1.0.0 / Version 1.0.0')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #64748b; font-size: 8pt;')
        layout.addWidget(version_label)
        
    def on_login(self):
        """Handle login button click"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # Validate inputs
        if not username:
            QMessageBox.warning(
                self,
                'خطأ - Error',
                'الرجاء إدخال اسم المستخدم\nPlease enter username'
            )
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(
                self,
                'خطأ - Error',
                'الرجاء إدخال كلمة المرور\nPlease enter password'
            )
            self.password_edit.setFocus()
            return
        
        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText('جاري التحقق... / Authenticating...')
        
        try:
            # Authenticate user
            self.user = self.auth_service.login(username, password)
            
            logger.info(f'تسجيل دخول ناجح للمستخدم: {username}')
            
            # Emit signal
            self.login_successful.emit(self.user)
            
            # Accept dialog
            self.accept()
            
        except AuthenticationError as e:
            logger.warning(f'فشل تسجيل الدخول: {username} - {str(e)}')
            QMessageBox.critical(
                self,
                'فشل تسجيل الدخول - Login Failed',
                str(e)
            )
            self.password_edit.clear()
            self.password_edit.setFocus()
            
        except Exception as e:
            logger.error(f'خطأ في تسجيل الدخول: {str(e)}', exc_info=True)
            QMessageBox.critical(
                self,
                'خطأ - Error',
                f'حدث خطأ أثناء تسجيل الدخول\nAn error occurred during login:\n{str(e)}'
            )
        
        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText('تسجيل الدخول / Login')
    
    def on_forgot_password(self):
        """Handle forgot password button click"""
        QMessageBox.information(
            self,
            'نسيت كلمة المرور - Forgot Password',
            'الرجاء الاتصال بمسؤول النظام لإعادة تعيين كلمة المرور\n'
            'Please contact system administrator to reset your password'
        )
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Prevent closing with Escape key
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
