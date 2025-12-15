"""
Enhanced Data Table Widget with Excel-like features
جدول بيانات محسن مع ميزات شبيهة بـ Excel
"""

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QAction
from typing import List, Dict, Any
import csv
from io import StringIO


class DataTableWidget(QTableWidget):
    """Enhanced table widget with copy/paste and Excel-like features"""
    
    # Signals
    data_changed = Signal()
    row_added = Signal(int)
    row_deleted = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_table()
        self.setup_shortcuts()
        
    def setup_table(self):
        """Setup table properties"""
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Enable alternating row colors
        self.setAlternatingRowColors(True)
        
        # Enable selection
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # Stretch last section
        self.horizontalHeader().setStretchLastSection(True)
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Copy
        copy_action = QAction(self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_selection)
        self.addAction(copy_action)
        
        # Paste
        paste_action = QAction(self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_from_clipboard)
        self.addAction(paste_action)
        
        # Cut
        cut_action = QAction(self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut_selection)
        self.addAction(cut_action)
        
        # Delete
        delete_action = QAction(self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selection)
        self.addAction(delete_action)
        
        # Select All
        select_all_action = QAction(self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.selectAll)
        self.addAction(select_all_action)
        
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        # Copy
        copy_action = menu.addAction('نسخ / Copy')
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_selection)
        
        # Paste
        paste_action = menu.addAction('لصق / Paste')
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_from_clipboard)
        
        # Cut
        cut_action = menu.addAction('قص / Cut')
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut_selection)
        
        menu.addSeparator()
        
        # Delete
        delete_action = menu.addAction('حذف / Delete')
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selection)
        
        menu.addSeparator()
        
        # Insert row
        insert_action = menu.addAction('إضافة صف / Insert Row')
        insert_action.triggered.connect(self.insert_row_at_selection)
        
        # Delete row
        delete_row_action = menu.addAction('حذف الصف / Delete Row')
        delete_row_action.triggered.connect(self.delete_selected_rows)
        
        menu.addSeparator()
        
        # Select all
        select_all_action = menu.addAction('تحديد الكل / Select All')
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.selectAll)
        
        menu.exec(self.viewport().mapToGlobal(position))
        
    def copy_selection(self):
        """Copy selected cells to clipboard"""
        selection = self.selectedRanges()
        if not selection:
            return
        
        # Get selected range
        sel_range = selection[0]
        
        # Build CSV-like text
        rows = []
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            cols = []
            for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                item = self.item(row, col)
                cols.append(item.text() if item else '')
            rows.append('\t'.join(cols))
        
        # Copy to clipboard
        clipboard_text = '\n'.join(rows)
        QApplication.clipboard().setText(clipboard_text)
        
    def paste_from_clipboard(self):
        """Paste from clipboard to selected cells"""
        clipboard_text = QApplication.clipboard().text()
        if not clipboard_text:
            return
        
        selection = self.selectedRanges()
        if not selection:
            # If no selection, paste at (0, 0)
            start_row, start_col = 0, 0
        else:
            sel_range = selection[0]
            start_row = sel_range.topRow()
            start_col = sel_range.leftColumn()
        
        # Parse clipboard as TSV
        rows = clipboard_text.split('\n')
        
        # Ensure enough rows
        required_rows = start_row + len(rows)
        if required_rows > self.rowCount():
            self.setRowCount(required_rows)
        
        # Paste data
        for i, row_text in enumerate(rows):
            if not row_text.strip():
                continue
                
            cols = row_text.split('\t')
            
            # Ensure enough columns
            required_cols = start_col + len(cols)
            if required_cols > self.columnCount():
                # Don't add columns automatically
                cols = cols[:self.columnCount() - start_col]
            
            for j, cell_text in enumerate(cols):
                row_idx = start_row + i
                col_idx = start_col + j
                
                if col_idx >= self.columnCount():
                    break
                
                item = self.item(row_idx, col_idx)
                if not item:
                    item = QTableWidgetItem()
                    self.setItem(row_idx, col_idx, item)
                
                item.setText(cell_text)
        
        self.data_changed.emit()
        
    def cut_selection(self):
        """Cut selected cells to clipboard"""
        self.copy_selection()
        self.delete_selection()
        
    def delete_selection(self):
        """Delete content of selected cells"""
        selection = self.selectedRanges()
        if not selection:
            return
        
        sel_range = selection[0]
        
        for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
            for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                item = self.item(row, col)
                if item:
                    item.setText('')
        
        self.data_changed.emit()
        
    def insert_row_at_selection(self):
        """Insert a new row at current selection"""
        current_row = self.currentRow()
        if current_row < 0:
            current_row = self.rowCount()
        
        self.insertRow(current_row)
        self.row_added.emit(current_row)
        
    def delete_selected_rows(self):
        """Delete selected rows"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        # Sort in reverse order to delete from bottom to top
        for row in sorted(selected_rows, reverse=True):
            self.removeRow(row)
            self.row_deleted.emit(row)
        
        self.data_changed.emit()
        
    def get_row_data(self, row: int) -> List[str]:
        """Get all data from a row"""
        data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            data.append(item.text() if item else '')
        return data
        
    def set_row_data(self, row: int, data: List[str]):
        """Set data for a row"""
        for col, value in enumerate(data):
            if col >= self.columnCount():
                break
            
            item = self.item(row, col)
            if not item:
                item = QTableWidgetItem()
                self.setItem(row, col, item)
            
            item.setText(str(value))
            
    def get_all_data(self) -> List[List[str]]:
        """Get all table data"""
        data = []
        for row in range(self.rowCount()):
            data.append(self.get_row_data(row))
        return data
        
    def set_all_data(self, data: List[List[str]]):
        """Set all table data"""
        self.setRowCount(len(data))
        for row, row_data in enumerate(data):
            self.set_row_data(row, row_data)
            
    def export_to_csv(self, filename: str):
        """Export table data to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # Write headers
            headers = []
            for col in range(self.columnCount()):
                header_item = self.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f'Column {col}')
            writer.writerow(headers)
            
            # Write data
            writer.writerows(self.get_all_data())
            
    def import_from_csv(self, filename: str):
        """Import table data from CSV file"""
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            # Skip header
            next(reader, None)
            
            # Read data
            data = list(reader)
            self.set_all_data(data)
            
        self.data_changed.emit()
