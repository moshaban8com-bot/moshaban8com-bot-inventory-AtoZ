# PySide6 UI Implementation Guide

## Overview

This document describes the complete PySide6 (Qt6) graphical user interface implementation for the Inventory Management System with full Arabic RTL support.

## Features Implemented

### ✅ Core Infrastructure
- **RTL Support**: Complete right-to-left layout for Arabic
- **Themes**: Dark and Light themes with QSS stylesheets
- **Font Support**: Cairo and Noto Naskh Arabic fonts
- **High DPI**: Automatic scaling for high-resolution displays

### ✅ Authentication & Session Management
- **Login Dialog**: Secure login with password hashing (bcrypt)
- **Company Selector**: Multi-company and multi-warehouse support
- **Session Management**: User session tracking with audit logs

### ✅ Main Window
- **Menu Bar**: Comprehensive menus in Arabic and English
  - File (ملف): Switch company/warehouse, Exit
  - Masters (البيانات الأساسية): Items, Categories, Warehouses, etc.
  - Documents (المستندات): GRN, Issue, Transfer, Adjustment, Stock Count
  - Manufacturing (التصنيع): BOM, Production Orders
  - Reports (التقارير): Reports Center
  - Settings (الإعدادات): Users, Roles, Policies
  - Help (مساعدة): About

- **Toolbar**: Quick access buttons with keyboard shortcuts
- **Sidebar**: Collapsible navigation panel
- **Status Bar**: Displays current user, company, warehouse, date/time
- **Tab-Based Interface**: Multiple screens open simultaneously

### ✅ Dashboard
- **KPI Cards**: 
  - Total Inventory Value
  - Total Items Count
  - Today's Movements
  - Items Below Reorder Point
- **Charts**: Placeholders for Top 10 items and warehouse distribution
- **Quick Actions**: Buttons for common operations

### ✅ Reusable Widgets

#### DataTableWidget
- Excel-like copy/paste functionality (Ctrl+C, Ctrl+V)
- Context menu with standard operations
- Keyboard shortcuts (Ctrl+C, Ctrl+V, Ctrl+X, Delete)
- Row insertion and deletion
- CSV export/import
- Alternating row colors
- Sortable columns

#### SearchBoxWidget
- Real-time search with debounce (300ms)
- Autocomplete support
- Clear button

#### ComboSearchWidget
- Searchable dropdown
- Filter as you type
- Data binding support

#### DatePickerWidget
- Calendar popup
- RTL calendar layout (Saturday as first day)
- Date range validation
- Multiple date formats

#### NotificationWidget
- Toast notifications (Success, Error, Warning, Info)
- Auto-dismiss after 3 seconds
- Fade in/out animations
- Color-coded by type

### ✅ Master Data Screens

#### Items Screen
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced search and filtering
- Table view with sortable columns
- Form dialog for add/edit with validation
- Fields:
  - Code, Name (AR/EN), Description
  - Category, UOM
  - Reorder point
  - Active status
- Integration with database models

### ✅ Document Screens

#### Base Document Screen
- Reusable base class for all documents
- Header section with common fields
- Editable lines grid with Excel-like features
- Automatic totals calculation
- Status management (Draft, Submitted, Approved, Posted, Cancelled)
- Action buttons (Save, Post, Cancel)
- Visual status indicators with colors

#### GRN Receipt Screen
- Extends base document
- Supplier selection
- Warehouse display
- Reference number
- Multiple line items with:
  - Item code and name
  - UOM
  - Quantity and price
  - Line totals
- Automatic quantity and amount totals

### ✅ Reports

#### Reports Center
- List of available reports
- Dynamic filter panel
- Common filters:
  - Date range (From/To)
  - Warehouse selection
  - Category selection
- Export options:
  - Preview
  - Excel export
  - PDF export
- Available reports:
  - Stock on Hand
  - Inventory Valuation
  - Item Card
  - Movement Summary
  - Reorder Report
  - Lot Traceability

## Architecture

### Directory Structure
```
ui/
├── __init__.py
├── login_dialog.py          # Login screen
├── company_selector.py      # Company/warehouse selection
├── main_window.py           # Main application window
├── dashboard.py             # Dashboard with KPIs
├── styles/
│   ├── __init__.py
│   ├── rtl_support.py       # RTL and theme management
│   ├── dark_theme.qss       # Dark theme stylesheet
│   └── light_theme.qss      # Light theme stylesheet
├── widgets/
│   ├── __init__.py
│   ├── data_table.py        # Enhanced table with Excel features
│   ├── search_box.py        # Search widget
│   ├── date_picker.py       # Date picker
│   ├── combo_search.py      # Searchable combo box
│   └── notification.py      # Toast notifications
├── masters/
│   ├── __init__.py
│   └── items_screen.py      # Items master data
├── documents/
│   ├── __init__.py
│   ├── base_document.py     # Base document screen
│   └── grn_receipt.py       # GRN receipt document
├── manufacturing/
│   └── __init__.py
├── reports/
│   ├── __init__.py
│   └── reports_center.py    # Reports center
├── settings/
│   └── __init__.py
├── import_export/
│   └── __init__.py
└── backup/
    └── __init__.py
```

### Design Patterns

#### Inheritance Hierarchy
- `BaseDocumentScreen` - Base class for all documents
  - `GRNReceiptScreen` - GRN specific implementation
  - Other document screens extend this

#### Signal/Slot Pattern
- All custom widgets emit signals for events
- Parent screens connect to these signals
- Example: `search_triggered`, `data_changed`, `document_saved`

#### Model-View Pattern
- Screens separate UI from business logic
- Database operations through `session_scope()`
- Data models from `data.models`

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Document |
| Ctrl+S | Save |
| Ctrl+P | Print |
| Ctrl+F | Search |
| Ctrl+C | Copy (in tables) |
| Ctrl+V | Paste (in tables) |
| Ctrl+X | Cut (in tables) |
| Delete | Delete selected |
| F5 | Refresh |
| F9 | Post Document |
| Esc | Close Current Tab |
| Ctrl+Q | Quit Application |

## Color Scheme

### Dark Theme
- Primary: `#2563eb` (Blue)
- Success: `#22c55e` (Green)
- Error: `#ef4444` (Red)
- Warning: `#f59e0b` (Orange)
- Info: `#06b6d4` (Cyan)
- Background: `#1e293b` (Dark Slate)
- Text: `#f8fafc` (Off White)

### Light Theme
- Primary: `#2563eb` (Blue)
- Success: `#22c55e` (Green)
- Error: `#ef4444` (Red)
- Warning: `#f59e0b` (Orange)
- Info: `#06b6d4` (Cyan)
- Background: `#f8fafc` (Light Gray)
- Text: `#1e293b` (Dark Slate)

## Integration with Backend

### Database
- Uses SQLAlchemy ORM
- `session_scope()` context manager for transactions
- Models from `data.models`

### Services
- `PostingService` - Document posting logic
- `CostingService` - Inventory costing
- `ValidationService` - Data validation
- `PolicyService` - Business rules

### Security
- `AuthService` - Authentication and session management
- Role-based access control (RBAC)
- Audit logging

## Running the Application

### Prerequisites
```bash
pip install -r requirements.txt
```

### Initialize Database
```bash
python -m data.seed
```

### Launch Application
```bash
python main.py
```

### Default Credentials
- Username: `admin`
- Password: `admin123`

## Testing

See `TESTING_UI.md` for comprehensive testing checklist.

## Future Enhancements

### Pending Screens
- [ ] Additional master screens (Categories, Warehouses, Locations, UOM, Suppliers, Customers)
- [ ] Document screens (Issue, Transfer, Adjustment, Stock Count)
- [ ] Manufacturing screens (BOM, Production Orders)
- [ ] Settings screens (Company Setup, Policies, Users, Roles, Sequences)
- [ ] Import/Export wizards
- [ ] Backup/Restore utilities

### Pending Features
- [ ] Actual chart rendering (using QtCharts or matplotlib)
- [ ] Report generation with actual data
- [ ] PDF export functionality
- [ ] Advanced search filters
- [ ] Batch operations
- [ ] Keyboard navigation enhancements
- [ ] Accessibility features
- [ ] Localization system for multi-language support

## Technical Notes

### RTL Support
- Application layout direction set to `Qt.RightToLeft`
- All text inputs support bidirectional text
- Tables and lists flow right-to-left
- Calendar starts on Saturday (common in Arabic countries)

### Performance
- Lazy loading for large datasets
- Database query optimization with proper indexing
- Table pagination for large result sets
- Debounced search to reduce database queries

### Extensibility
- Base classes for common patterns
- Plugin architecture ready for custom screens
- Theme system supports custom themes
- Widget library for consistent UI

## Troubleshooting

### Display Issues
- If running in headless environment, install virtual display:
  ```bash
  sudo apt-get install xvfb
  xvfb-run python main.py
  ```

### Font Issues
- Ensure Cairo or Noto Naskh Arabic fonts are installed
- Fallback to Arial/Segoe UI if custom fonts unavailable

### Database Issues
- Check database file exists: `data/inventory.db`
- Re-run seed script if database is corrupt

## License

Copyright © 2024. All Rights Reserved.
