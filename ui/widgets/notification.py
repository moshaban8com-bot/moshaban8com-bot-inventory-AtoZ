"""
Toast Notification Widget
إشعارات منبثقة
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtGui import QPainter, QPainterPath


class NotificationWidget(QWidget):
    """Toast notification widget"""
    
    def __init__(self, message, notification_type='info', parent=None):
        super().__init__(parent)
        
        self.notification_type = notification_type
        self.setup_ui(message)
        self.setup_animation()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, self.fade_out)
        
    def setup_ui(self, message):
        """Setup user interface"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon/Type indicator
        type_label = QLabel()
        if self.notification_type == 'success':
            type_label.setText('✓')
            type_label.setStyleSheet('color: #22c55e; font-size: 18pt; font-weight: bold;')
        elif self.notification_type == 'error':
            type_label.setText('✗')
            type_label.setStyleSheet('color: #ef4444; font-size: 18pt; font-weight: bold;')
        elif self.notification_type == 'warning':
            type_label.setText('⚠')
            type_label.setStyleSheet('color: #f59e0b; font-size: 18pt; font-weight: bold;')
        else:  # info
            type_label.setText('ℹ')
            type_label.setStyleSheet('color: #2563eb; font-size: 18pt; font-weight: bold;')
        
        layout.addWidget(type_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet('color: white; font-size: 11pt;')
        layout.addWidget(message_label)
        
        # Style based on type
        if self.notification_type == 'success':
            bg_color = '#22c55e'
        elif self.notification_type == 'error':
            bg_color = '#ef4444'
        elif self.notification_type == 'warning':
            bg_color = '#f59e0b'
        else:
            bg_color = '#2563eb'
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)
        
        # Set size
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.adjustSize()
        
    def setup_animation(self):
        """Setup fade-in animation"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(200)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.start()
        
    def fade_out(self):
        """Fade out and close"""
        fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_out_animation.setDuration(200)
        fade_out_animation.setStartValue(1.0)
        fade_out_animation.setEndValue(0.0)
        fade_out_animation.finished.connect(self.close)
        fade_out_animation.start()
        
    def show_notification(self):
        """Show notification at bottom-right of parent"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.bottom() - self.height() - 20
            self.move(x, y)
        
        self.show()


def show_success(parent, message):
    """Show success notification"""
    notification = NotificationWidget(message, 'success', parent)
    notification.show_notification()
    return notification


def show_error(parent, message):
    """Show error notification"""
    notification = NotificationWidget(message, 'error', parent)
    notification.show_notification()
    return notification


def show_warning(parent, message):
    """Show warning notification"""
    notification = NotificationWidget(message, 'warning', parent)
    notification.show_notification()
    return notification


def show_info(parent, message):
    """Show info notification"""
    notification = NotificationWidget(message, 'info', parent)
    notification.show_notification()
    return notification
