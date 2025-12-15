"""
Date Picker Widget
منتقي التاريخ
"""

from PySide6.QtWidgets import QDateEdit, QCalendarWidget
from PySide6.QtCore import Qt, Signal, QDate


class DatePickerWidget(QDateEdit):
    """Enhanced date picker widget"""
    
    # Signals
    date_changed = Signal(object)  # Emits QDate
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_widget()
        self.dateChanged.connect(self.on_date_changed)
        
    def setup_widget(self):
        """Setup widget properties"""
        # Set calendar popup
        self.setCalendarPopup(True)
        
        # Set display format
        self.setDisplayFormat('yyyy-MM-dd')
        
        # Set current date as default
        self.setDate(QDate.currentDate())
        
        # Set date range (allow dates from 2000 to 2100)
        self.setMinimumDate(QDate(2000, 1, 1))
        self.setMaximumDate(QDate(2100, 12, 31))
        
        # Customize calendar
        calendar = QCalendarWidget()
        calendar.setFirstDayOfWeek(Qt.Saturday)  # Set first day of week
        calendar.setGridVisible(True)
        self.setCalendarWidget(calendar)
        
    def on_date_changed(self, date):
        """Handle date change"""
        self.date_changed.emit(date)
        
    def get_date(self):
        """Get selected date as QDate"""
        return self.date()
        
    def get_date_string(self, format='yyyy-MM-dd'):
        """Get selected date as string"""
        return self.date().toString(format)
        
    def set_date(self, date):
        """Set date (accepts QDate or string in yyyy-MM-dd format)"""
        if isinstance(date, str):
            date = QDate.fromString(date, 'yyyy-MM-dd')
        self.setDate(date)
        
    def set_today(self):
        """Set to today's date"""
        self.setDate(QDate.currentDate())
