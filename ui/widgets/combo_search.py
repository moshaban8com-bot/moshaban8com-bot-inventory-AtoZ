"""
ComboBox with Search Widget
ComboBox مع إمكانية البحث
"""

from PySide6.QtWidgets import QComboBox, QCompleter
from PySide6.QtCore import Qt, Signal


class ComboSearchWidget(QComboBox):
    """ComboBox with search/filter capability"""
    
    # Signals
    selection_changed = Signal(object)  # Emits selected data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_search()
        self.currentIndexChanged.connect(self.on_selection_changed)
        
    def setup_search(self):
        """Setup search/filter capability"""
        # Make it editable for searching
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # Setup completer
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)
        
    def add_item(self, text, data=None):
        """Add item with optional data"""
        self.addItem(text, data)
        
    def add_items_with_data(self, items):
        """
        Add multiple items with data
        
        Args:
            items: List of tuples (text, data)
        """
        for text, data in items:
            self.addItem(text, data)
            
    def get_selected_data(self):
        """Get data of selected item"""
        return self.currentData()
        
    def set_selected_by_data(self, data):
        """Set selection by data value"""
        for i in range(self.count()):
            if self.itemData(i) == data:
                self.setCurrentIndex(i)
                return True
        return False
        
    def on_selection_changed(self, index):
        """Handle selection change"""
        if index >= 0:
            self.selection_changed.emit(self.currentData())
            
    def clear_items(self):
        """Clear all items"""
        self.clear()
