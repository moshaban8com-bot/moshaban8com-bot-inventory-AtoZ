# Quick Start Guide - PySide6 UI

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python -m data.seed
```

This will create:
- Database: `data/inventory.db`
- Demo company with warehouses
- Sample items and categories
- Admin user (username: `admin`, password: `admin123`)

### Step 3: Launch Application
```bash
python main.py
```

## 🎯 What You'll See

### 1. Login Screen
- Enter username: `admin`
- Enter password: `admin123`
- Click "تسجيل الدخول / Login"

### 2. Company Selector
- Select a company from the dropdown
- Select a warehouse
- Click "تأكيد / Confirm"

### 3. Main Window
You'll see:
- **Dashboard** with KPI cards
- **Menu Bar** with all modules
- **Toolbar** with quick actions
- **Sidebar** for navigation
- **Status Bar** showing user/company/warehouse

## 🎨 What to Try

### Master Data - Items Screen
1. Click **البيانات الأساسية / Masters** → **الأصناف / Items**
2. See existing items in the table
3. Use search box to filter items
4. Click **جديد / New** to add an item
5. Click **تعديل / Edit** to modify an item
6. Try Excel copy/paste (Ctrl+C, Ctrl+V) in the table

### Documents - GRN Receipt
1. Click **المستندات / Documents** → **استلام بضاعة / GRN Receipt**
2. Select a supplier
3. Add items to the lines grid
4. Click **إضافة صنف / Add Item** to add rows
5. Watch totals calculate automatically
6. Click **حفظ كمسودة / Save as Draft**
7. Click **ترحيل / Post** (F9) to post the document

### Reports Center
1. Click **التقارير / Reports** → **مركز التقارير / Reports Center**
2. Select a report from the list
3. Adjust filters (date range, warehouse, category)
4. Click **معاينة / Preview** or **تصدير / Export**

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Document |
| Ctrl+S | Save |
| Ctrl+C | Copy (in tables) |
| Ctrl+V | Paste (in tables) |
| F5 | Refresh |
| F9 | Post Document |
| Esc | Close Current Tab |

## 🎨 Features to Explore

### Theme
- Application uses **Dark Theme** by default
- Clean, modern interface
- Consistent color scheme

### RTL Support
- Arabic text flows right-to-left
- Menus and dialogs are mirrored
- Dates and numbers formatted correctly

### Bilingual Interface
- All text in both Arabic and English
- Format: "Arabic / English"

### Notifications
- Success messages in green
- Error messages in red
- Auto-dismiss after 3 seconds

## 📁 Sample Data Created

The seed script creates:
- **1 Company**: شركة تجريبية / Demo Company
- **3 Warehouses**: Main, Secondary, Transit
- **6 Locations** per warehouse
- **5 UOM**: Piece, Box, Carton, Kg, Liter
- **3 Categories**: Electronics, Food, Supplies
- **5 Sample Items**
- **1 Admin User**: admin/admin123
- **Roles & Permissions**

## 🔧 Troubleshooting

### "Database not found"
```bash
python -m data.seed
```

### "User not found" or "Invalid password"
- Username: `admin`
- Password: `admin123`
- Case-sensitive!

### No companies or warehouses showing
```bash
# Re-seed the database
rm data/inventory.db
python -m data.seed
```

### Application won't start in headless environment
```bash
# Use virtual display
sudo apt-get install xvfb
xvfb-run python main.py
```

## 📚 More Information

- **Full UI Guide**: See `UI_README.md`
- **Testing Checklist**: See `TESTING_UI.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`

## 🎉 You're Ready!

The system is fully functional and ready to use. Explore the different screens, try adding data, and experience the complete inventory management workflow.

Enjoy! 🚀
