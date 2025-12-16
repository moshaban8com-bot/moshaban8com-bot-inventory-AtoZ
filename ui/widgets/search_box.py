"""
Advanced Search Box Widget
مربع بحث متقدم
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QCompleter
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon


class SearchBoxWidget(QWidget):
    """Advanced search box with autocomplete and debounce"""
    
    # Signals
    search_triggered = Signal(str)  # Emits search text
    search_cleared = Signal()
    
    def __init__(self, placeholder='بحث... / Search...', parent=None):
        super().__init__(parent)
        
        self.search_delay = 300  # milliseconds
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search)
        
        self.setup_ui(placeholder)
        
    def setup_ui(self, placeholder):
        """Setup user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.on_text_changed)
        self.search_input.returnPressed.connect(self._emit_search)
        layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton('بحث / Search')
        self.search_button.clicked.connect(self._emit_search)
        layout.addWidget(self.search_button)
        
        # Clear button
        self.clear_button = QPushButton('مسح / Clear')
        self.clear_button.setProperty('secondary', True)
        self.clear_button.clicked.connect(self.clear_search)
        layout.addWidget(self.clear_button)
        
    def on_text_changed(self, text):
        """Handle text change with debounce"""
        # Restart timer on each text change
        self.search_timer.stop()
        if text:
            self.search_timer.start(self.search_delay)
        else:
            self.search_cleared.emit()
            
    def _emit_search(self):
        """Emit search signal"""
        search_text = self.search_input.text().strip()
        if search_text:
            self.search_triggered.emit(search_text)
            
    def clear_search(self):
        """Clear search input"""
        self.search_input.clear()
        self.search_cleared.emit()
        
    def set_completer(self, items):
        """Set autocomplete items"""
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(completer)
        
    def get_text(self):
        """Get current search text"""
        return self.search_input.text().strip()
        
    def set_text(self, text):
        """Set search text"""
        self.search_input.setText(text)
