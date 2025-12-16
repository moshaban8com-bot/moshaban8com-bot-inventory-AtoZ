# Testing the PySide6 UI

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database and seed with test data:
```bash
python -m data.seed
```

## Running the Application

```bash
python main.py
```

## Test Credentials

- **Username:** admin
- **Password:** admin123

## Testing Checklist

### Login Flow
- [ ] Login dialog appears with RTL layout
- [ ] Can enter username and password
- [ ] Login with correct credentials succeeds
- [ ] Login with incorrect credentials shows error

### Company/Warehouse Selection
- [ ] Company selector shows available companies
- [ ] Warehouse combo populates based on selected company
- [ ] Can confirm selection and proceed to main window

### Main Window
- [ ] Main window opens maximized
- [ ] Menu bar is visible with Arabic/English menus
- [ ] Toolbar shows action buttons
- [ ] Sidebar shows navigation items
- [ ] Status bar shows user, company, warehouse info
- [ ] Dark theme is applied

### Dashboard
- [ ] Dashboard loads by default
- [ ] KPI cards show data
- [ ] Quick action buttons are visible

### Items Screen
- [ ] Can open Items screen from menu or sidebar
- [ ] Table shows existing items
- [ ] Search box filters items
- [ ] Can add new item
- [ ] Can edit existing item
- [ ] Can delete item (with confirmation)
- [ ] Refresh button works

### GRN Receipt Screen
- [ ] Can open GRN screen from menu
- [ ] Header section shows supplier combo
- [ ] Lines table is editable
- [ ] Can add/remove lines
- [ ] Totals calculate automatically
- [ ] Can save as draft
- [ ] Can post document
- [ ] Status changes correctly

### Reports Center
- [ ] Can open Reports Center from menu
- [ ] Reports list shows available reports
- [ ] Selecting report shows filters
- [ ] Filter controls are functional
- [ ] Export buttons are visible

### General UI Features
- [ ] RTL layout works correctly
- [ ] Arabic text displays properly
- [ ] Keyboard shortcuts work (Ctrl+N, Ctrl+S, F5, F9, etc.)
- [ ] Tab navigation works
- [ ] Can close tabs
- [ ] Multiple screens can be open simultaneously
- [ ] Notifications appear when actions complete

### Theme
- [ ] Dark theme is consistent across all screens
- [ ] Colors match the specification
- [ ] Buttons have correct colors (success=green, danger=red, etc.)
- [ ] Status labels have correct colors

## Known Issues

- Charts in dashboard are placeholders
- Some master screens are not yet implemented
- Document posting doesn't update database yet
- Reports don't generate actual data yet
