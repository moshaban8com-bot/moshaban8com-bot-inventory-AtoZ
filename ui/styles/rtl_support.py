"""
RTL Support and Theme Management
دعم الكتابة من اليمين لليسار وإدارة السمات
"""

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication
from pathlib import Path
from config import APP_CONFIG, RESOURCES_CONFIG


def setup_rtl(app: QApplication):
    """
    Setup RTL (Right-to-Left) support for Arabic
    
    Args:
        app: QApplication instance
    """
    # Set RTL layout direction
    if APP_CONFIG.get('rtl', True):
        app.setLayoutDirection(Qt.RightToLeft)
    
    # Load and set Arabic font
    load_arabic_font(app)
    
    # Set application-wide attributes
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def load_arabic_font(app: QApplication):
    """
    Load Arabic fonts (Cairo or Noto Naskh Arabic)
    
    Args:
        app: QApplication instance
    """
    fonts_dir = RESOURCES_CONFIG.get('fonts_dir')
    
    # Try to load Cairo font
    font_families = ['Cairo', 'Noto Naskh Arabic', 'Arial', 'Segoe UI']
    
    # If custom fonts exist in fonts directory, load them
    if fonts_dir and fonts_dir.exists():
        for font_file in fonts_dir.glob('*.ttf'):
            QFontDatabase.addApplicationFont(str(font_file))
        for font_file in fonts_dir.glob('*.otf'):
            QFontDatabase.addApplicationFont(str(font_file))
    
    # Try each font family in order
    font_size = APP_CONFIG.get('font_size', 10)
    for family in font_families:
        font = QFont(family, font_size)
        if QFontDatabase.hasFamily(family):
            app.setFont(font)
            break
    else:
        # Fallback to default font
        font = QFont(APP_CONFIG.get('font_family', 'Arial'), font_size)
        app.setFont(font)


def load_theme(theme_name: str = 'dark') -> str:
    """
    Load theme stylesheet
    
    Args:
        theme_name: 'dark' or 'light'
        
    Returns:
        QSS stylesheet string
    """
    # Get the styles directory
    styles_dir = Path(__file__).parent
    
    # Load theme file
    if theme_name == 'dark':
        theme_file = styles_dir / 'dark_theme.qss'
    elif theme_name == 'light':
        theme_file = styles_dir / 'light_theme.qss'
    else:
        return ''
    
    if theme_file.exists():
        with open(theme_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    return get_default_dark_theme() if theme_name == 'dark' else get_default_light_theme()


def get_default_dark_theme() -> str:
    """Get default dark theme if file doesn't exist"""
    return """
    /* Default Dark Theme */
    QMainWindow, QDialog, QWidget {
        background-color: #1e293b;
        color: #f8fafc;
    }
    
    QPushButton {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #1d4ed8;
    }
    
    QPushButton:pressed {
        background-color: #1e40af;
    }
    
    QPushButton:disabled {
        background-color: #475569;
        color: #94a3b8;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
        background-color: #334155;
        color: #f8fafc;
        border: 1px solid #475569;
        padding: 6px;
        border-radius: 4px;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #2563eb;
    }
    
    QComboBox {
        background-color: #334155;
        color: #f8fafc;
        border: 1px solid #475569;
        padding: 6px;
        border-radius: 4px;
    }
    
    QComboBox:hover {
        border: 1px solid #2563eb;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QTableWidget, QTableView {
        background-color: #334155;
        alternate-background-color: #2d3748;
        color: #f8fafc;
        gridline-color: #475569;
        border: 1px solid #475569;
    }
    
    QTableWidget::item:selected, QTableView::item:selected {
        background-color: #2563eb;
    }
    
    QHeaderView::section {
        background-color: #475569;
        color: #f8fafc;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
    
    QMenuBar {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    QMenuBar::item:selected {
        background-color: #2563eb;
    }
    
    QMenu {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #475569;
    }
    
    QMenu::item:selected {
        background-color: #2563eb;
    }
    
    QStatusBar {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    QToolBar {
        background-color: #0f172a;
        border: none;
        spacing: 4px;
    }
    
    QTabWidget::pane {
        border: 1px solid #475569;
        background-color: #1e293b;
    }
    
    QTabBar::tab {
        background-color: #334155;
        color: #f8fafc;
        padding: 8px 16px;
        border: 1px solid #475569;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #2563eb;
    }
    
    QScrollBar:vertical {
        background-color: #334155;
        width: 12px;
        border: none;
    }
    
    QScrollBar::handle:vertical {
        background-color: #475569;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #64748b;
    }
    
    QScrollBar:horizontal {
        background-color: #334155;
        height: 12px;
        border: none;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #475569;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #64748b;
    }
    """


def get_default_light_theme() -> str:
    """Get default light theme if file doesn't exist"""
    return """
    /* Default Light Theme */
    QMainWindow, QDialog, QWidget {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    QPushButton {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #1d4ed8;
    }
    
    QPushButton:pressed {
        background-color: #1e40af;
    }
    
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #64748b;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
        background-color: white;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        padding: 6px;
        border-radius: 4px;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #2563eb;
    }
    
    QComboBox {
        background-color: white;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        padding: 6px;
        border-radius: 4px;
    }
    
    QComboBox:hover {
        border: 1px solid #2563eb;
    }
    
    QTableWidget, QTableView {
        background-color: white;
        alternate-background-color: #f1f5f9;
        color: #1e293b;
        gridline-color: #cbd5e1;
        border: 1px solid #cbd5e1;
    }
    
    QTableWidget::item:selected, QTableView::item:selected {
        background-color: #2563eb;
        color: white;
    }
    
    QHeaderView::section {
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
    
    QMenuBar {
        background-color: white;
        color: #1e293b;
        border-bottom: 1px solid #cbd5e1;
    }
    
    QMenuBar::item:selected {
        background-color: #2563eb;
        color: white;
    }
    
    QMenu {
        background-color: white;
        color: #1e293b;
        border: 1px solid #cbd5e1;
    }
    
    QMenu::item:selected {
        background-color: #2563eb;
        color: white;
    }
    
    QStatusBar {
        background-color: #f1f5f9;
        color: #1e293b;
        border-top: 1px solid #cbd5e1;
    }
    
    QToolBar {
        background-color: #f1f5f9;
        border: none;
        spacing: 4px;
    }
    
    QTabWidget::pane {
        border: 1px solid #cbd5e1;
        background-color: white;
    }
    
    QTabBar::tab {
        background-color: #e2e8f0;
        color: #1e293b;
        padding: 8px 16px;
        border: 1px solid #cbd5e1;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        color: #2563eb;
    }
    """
