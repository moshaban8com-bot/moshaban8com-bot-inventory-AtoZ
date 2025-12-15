# دليل الإعداد والتثبيت (Setup Guide)

## متطلبات النظام (System Requirements)

### البرامج المطلوبة (Required Software)
- Python 3.11 أو أحدث
- Windows 10/11 (للاستخدام كتطبيق سطح مكتب)
- 4 GB RAM (الحد الأدنى)
- 500 MB مساحة تخزين

## خطوات التثبيت (Installation Steps)

### 1. تثبيت Python

قم بتحميل Python من الموقع الرسمي:
- https://www.python.org/downloads/

تأكد من تحديد خيار "Add Python to PATH" أثناء التثبيت

### 2. استنساخ المشروع (Clone Repository)

```bash
git clone https://github.com/moshaban8com-bot/moshaban8com-bot-inventory-AtoZ.git
cd moshaban8com-bot-inventory-AtoZ
```

### 3. إنشاء بيئة افتراضية (Virtual Environment)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 4. تثبيت المتطلبات (Install Dependencies)

```bash
pip install -r requirements.txt
```

### 5. إنشاء قاعدة البيانات والبيانات التجريبية

```bash
python -m data.seed
```

سيتم إنشاء:
- قاعدة بيانات SQLite في `data/inventory.db`
- شركة تجريبية
- مخزن رئيسي
- أصناف تجريبية
- مستخدم مدير (admin / admin123)

### 6. تشغيل التطبيق

```bash
python main.py
```

## اختبار النظام (Testing)

### تشغيل الاختبارات الأساسية

```bash
python test_system.py
```

يجب أن تنجح جميع الاختبارات (3/3):
- ✅ المصادقة (Authentication)
- ✅ الترحيل (Posting)
- ✅ التكلفة (Costing)

### تشغيل اختبارات التقارير

```bash
python test_reports.py
```

سيتم إنشاء ملفات Excel و CSV في `/tmp`:
- `stock_report.xlsx` - تقرير الأرصدة بصيغة Excel
- `stock_report.csv` - تقرير الأرصدة بصيغة CSV

## بناء ملف تنفيذي (Build Executable)

### استخدام PyInstaller

```bash
pyinstaller inventory.spec
```

سيتم إنشاء ملف `InventorySystem.exe` في مجلد `dist/`

### ملاحظات البناء
- تأكد من وجود جميع الملفات المطلوبة في مجلد `resources`
- الملف التنفيذي سيكون standalone ولا يحتاج Python مثبت

## الإعدادات (Configuration)

### تكوين قاعدة البيانات

قم بتحرير ملف `config.py` لتغيير إعدادات قاعدة البيانات:

```python
DATABASE_CONFIG = {
    'default': 'sqlite',  # أو 'postgresql'
    'sqlite': {
        'path': BASE_DIR / 'data' / 'inventory.db',
    },
    'postgresql': {
        'host': 'localhost',
        'port': '5432',
        'database': 'inventory',
        'user': 'postgres',
        'password': 'your_password',
    }
}
```

### إعدادات التطبيق

```python
APP_CONFIG = {
    'name': 'نظام إدارة المخزون',
    'rtl': True,  # Right-to-left للعربية
    'language': 'ar',
    'font_family': 'Cairo',
    'font_size': 10,
}
```

## استخدام PostgreSQL بدلاً من SQLite

### 1. تثبيت PostgreSQL

قم بتحميل وتثبيت PostgreSQL من:
- https://www.postgresql.org/download/

### 2. إنشاء قاعدة البيانات

```sql
CREATE DATABASE inventory;
CREATE USER inventory_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE inventory TO inventory_user;
```

### 3. تحديث المتغيرات البيئية

**Windows:**
```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=inventory
set DB_USER=inventory_user
set DB_PASSWORD=your_password
```

**Linux/Mac:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=inventory
export DB_USER=inventory_user
export DB_PASSWORD=your_password
```

### 4. تحديث config.py

```python
DATABASE_CONFIG = {
    'default': 'postgresql',  # تغيير من sqlite
    # ... باقي الإعدادات
}
```

### 5. إعادة إنشاء البيانات

```bash
python -m data.seed
```

## حل المشاكل (Troubleshooting)

### خطأ "ModuleNotFoundError"

تأكد من تثبيت جميع المتطلبات:
```bash
pip install -r requirements.txt
```

### خطأ في قاعدة البيانات

احذف قاعدة البيانات وأعد إنشاءها:
```bash
rm data/inventory.db
python -m data.seed
```

### مشاكل في الترميز العربي

تأكد من:
- استخدام UTF-8 encoding
- تثبيت الخطوط العربية على النظام
- تفعيل RTL في الإعدادات

### خطأ في PyInstaller

تأكد من:
- تحديث PyInstaller: `pip install --upgrade pyinstaller`
- وجود جميع الملفات المطلوبة
- عدم وجود مسافات في مسار المشروع

## النسخ الاحتياطي والاستعادة (Backup & Restore)

### نسخ احتياطي لقاعدة البيانات

**SQLite:**
```bash
cp data/inventory.db backups/inventory_backup_$(date +%Y%m%d).db
```

**PostgreSQL:**
```bash
pg_dump -U inventory_user inventory > backups/inventory_backup_$(date +%Y%m%d).sql
```

### استعادة من نسخة احتياطية

**SQLite:**
```bash
cp backups/inventory_backup_YYYYMMDD.db data/inventory.db
```

**PostgreSQL:**
```bash
psql -U inventory_user inventory < backups/inventory_backup_YYYYMMDD.sql
```

## الدعم والمساعدة (Support)

للحصول على المساعدة:
1. راجع ملف README.md
2. افتح Issue على GitHub
3. راجع السجلات في `logs/inventory.log`

## الترخيص (License)

هذا المشروع مرخص تحت MIT License
