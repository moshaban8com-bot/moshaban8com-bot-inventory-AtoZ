# نظام إدارة المخزون المتكامل (Inventory Management System)

<div dir="rtl">

## نظرة عامة

نظام احترافي لإدارة المخزون مبني باستخدام PySide6 (Qt6) للعمل كتطبيق سطح مكتب على Windows.

### الميزات الرئيسية

- ✅ **دعم متعدد الشركات والمخازن** - Multi-Company & Multi-Warehouse
- ✅ **إدارة المخزون الكاملة** - Complete Inventory Management
- ✅ **وحدة التصنيع (اختيارية)** - Manufacturing Module
- ✅ **تتبع الحركة والتكلفة** - Movement Tracking & Costing
- ✅ **السياسات المرنة** - Flexible Policies
- ✅ **الأمان والصلاحيات** - Security & Permissions
- ✅ **واجهة عربية بالكامل** - Full Arabic UI (RTL)

</div>

---

## 🚀 Installation / التثبيت

### Requirements / المتطلبات

- Python 3.11 or higher
- Windows 10/11 (للتشغيل كتطبيق سطح مكتب)

### Setup / الإعداد

1. **Clone the repository / استنساخ المشروع:**
```bash
git clone https://github.com/moshaban8com-bot/moshaban8com-bot-inventory-AtoZ.git
cd moshaban8com-bot-inventory-AtoZ
```

2. **Create virtual environment / إنشاء بيئة افتراضية:**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. **Install dependencies / تثبيت المتطلبات:**
```bash
pip install -r requirements.txt
```

4. **Initialize database with demo data / إنشاء قاعدة البيانات والبيانات التجريبية:**
```bash
python -m data.seed
```

5. **Run the application / تشغيل التطبيق:**
```bash
python main.py
```

---

## 📁 Project Structure / هيكل المشروع

```
inventory-AtoZ/
├── config.py              # Configuration settings
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
│
├── data/                  # Database models & ORM
│   ├── __init__.py
│   ├── database.py       # Database connection & session
│   ├── models.py         # Core models (Company, Item, Warehouse, etc.)
│   ├── documents.py      # Document models (GRN, Issue, Transfer, etc.)
│   ├── security.py       # Security models (User, Role, Permission)
│   ├── policies.py       # Policy & Manufacturing models
│   └── seed.py           # Demo data creation
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── posting.py        # Document posting service
│   ├── costing.py        # Average costing service
│   ├── validation.py     # Business rule validation
│   └── policy.py         # Policy resolution service
│
├── security/              # Authentication & authorization
│   ├── __init__.py
│   └── auth.py           # Auth service
│
├── ui/                    # PySide6 UI components
│   └── (To be implemented)
│
├── reports/               # Report queries & definitions
│   └── (To be implemented)
│
├── import_export/         # Excel/CSV import/export
│   └── (To be implemented)
│
├── utils/                 # Helper utilities
│   ├── __init__.py
│   ├── logging.py        # Logging setup
│   ├── dates.py          # Date utilities
│   └── formatting.py     # Number formatting
│
├── resources/             # Icons, fonts, styles
│   ├── icons/
│   ├── fonts/
│   └── styles/
│
└── tests/                 # Unit tests
    └── (To be implemented)
```

---

## 🗄️ Database Schema / مخطط قاعدة البيانات

### Core Tables / الجداول الأساسية

- **companies** - الشركات
- **company_modules** - وحدات الشركة (Inventory, Manufacturing, etc.)
- **warehouses** - المخازن
- **locations** - المواقع داخل المخازن (Zone/Rack/Shelf/Bin)

### Master Data / البيانات الرئيسية

- **items** - الأصناف
- **item_categories** - تصنيفات الأصناف
- **uoms** - وحدات القياس
- **item_uom_conversions** - تحويلات وحدات القياس
- **barcodes** - الباركود
- **suppliers** - الموردون
- **customers** - العملاء

### Documents / المستندات

- **documents_header** - رؤوس المستندات
- **documents_lines** - بنود المستندات
- **doc_sequences** - تسلسل أرقام المستندات

### Inventory Ledger / دفتر الحركة

- **inventory_ledger** - دفتر حركة المخزون (المصدر الوحيد للحقيقة)
- **stock_balance** - أرصدة المخزون (Cache)

### Tracking / التتبع

- **lots** - أرقام التشغيلات
- **serials** - الأرقام التسلسلية

### Security / الأمان

- **users** - المستخدمون
- **roles** - الأدوار
- **permissions** - الصلاحيات
- **role_permissions** - صلاحيات الأدوار
- **user_roles** - أدوار المستخدمين
- **audit_log** - سجل المراجعة

### Policies / السياسات

- **policies** - السياسات (Global/Company/Warehouse/Item level)

### Manufacturing / التصنيع

- **boms** - قوائم المواد (Bill of Materials)
- **bom_lines** - بنود قوائم المواد
- **work_centers** - مراكز العمل
- **routings** - مسارات الإنتاج
- **production_orders** - أوامر الإنتاج

---

## 📋 Document Types / أنواع المستندات

1. **GRN_RECEIPT** - استلام بضاعة (Goods Receipt)
2. **ISSUE** - صرف (Issue)
3. **TRANSFER** - تحويل (Transfer between warehouses)
4. **ADJUSTMENT** - تسوية (Stock Adjustment)
5. **RETURN_IN** - مرتجع استلام (Return to Supplier)
6. **RETURN_OUT** - مرتجع صرف (Return from Customer)
7. **STOCK_COUNT** - جرد (Physical Stock Count)
8. **PRODUCTION_ORDER** - أمر إنتاج
9. **PRODUCTION_ISSUE** - صرف للإنتاج
10. **PRODUCTION_RECEIPT** - استلام من الإنتاج

---

## 🔄 Document Workflow / سير عمل المستندات

```
DRAFT → SUBMITTED → APPROVED → POSTED → (CANCELLED/REVERSED)
```

- **DRAFT** - مسودة
- **SUBMITTED** - مُقدّم
- **APPROVED** - مُعتمد
- **POSTED** - مُرحّل (Posted to Ledger)
- **CANCELLED** - مُلغى
- **REVERSED** - مُعكوس

---

## 💰 Costing Method / طريقة التكلفة

**Average Cost** - متوسط التكلفة (الافتراضي)

- عند الاستلام: تحديث متوسط التكلفة
- عند الصرف: القيمة = الكمية × متوسط التكلفة

---

## 🔐 Security & Authentication / الأمان والمصادقة

### Default Login Credentials / بيانات الدخول الافتراضية

بعد تشغيل `python -m data.seed`:

- **Username / اسم المستخدم:** `admin`
- **Password / كلمة المرور:** `admin123`

### Features / الميزات

- Password hashing using bcrypt
- Session management with timeout
- Role-based access control (RBAC)
- Company and warehouse level access control
- Audit trail for all operations
- Login attempt tracking and account lockout

---

## 📊 Inventory Policies / سياسات المخزون

يدعم النظام السياسات التالية مع تدرج هرمي (Item → Category → DOCTYPE → Warehouse → Company → Global):

1. **BLOCK_NEGATIVE_STOCK** - منع الأرصدة السالبة
2. **ALLOW_NEGATIVE_WITH_APPROVAL** - السماح بالأرصدة السالبة بموافقة
3. **BLOCK_ISSUE_FROM_EMPTY_LOCATION** - منع الصرف من موقع فارغ
4. **ENFORCE_SERIAL_TRACKING** - إلزام تتبع الأرقام التسلسلية
5. **ENFORCE_LOT_TRACKING** - إلزام تتبع أرقام التشغيلة
6. **FEFO_PICKING** - الصرف حسب تاريخ الانتهاء (اختياري)
7. **LOCK_POSTED_DOCUMENTS** - قفل المستندات المُرحّلة
8. **REQUIRE_REASON_CODE_FOR_ADJUSTMENTS** - طلب سبب التسوية

---

## 🏗️ Manufacturing Module / وحدة التصنيع

عند تفعيل وحدة التصنيع للشركة:

- **BOM (Bill of Materials)** - قوائم المواد مع الإصدارات
- **Work Centers** - مراكز العمل
- **Routings** - مسارات التصنيع
- **Production Orders** - أوامر الإنتاج
- **Material Issue to Production** - صرف مواد للإنتاج
- **Production Receipt** - استلام من الإنتاج
- **Scrap/Rework** - الهالك/إعادة التشغيل

---

## 🧪 Testing / الاختبار

```bash
# Run tests (To be implemented)
pytest

# Run with coverage
pytest --cov=.
```

---

## 📦 Building Executable / بناء ملف تنفيذي

```bash
# Using PyInstaller (To be implemented)
pyinstaller inventory.spec
```

سيتم إنشاء ملف `.exe` في مجلد `dist/`

---

## 🛠️ Development Status / حالة التطوير

### ✅ Completed / مكتمل

- [x] Project structure and configuration
- [x] Database models (SQLAlchemy ORM)
- [x] Core services (Posting, Costing, Validation, Policy)
- [x] Authentication system
- [x] Seed data script
- [x] Utility functions

### 🚧 In Progress / قيد التطوير

- [ ] PySide6 UI screens
- [ ] Reports system
- [ ] Import/Export functionality
- [ ] Unit tests
- [ ] PyInstaller packaging

### 📋 Planned / مخطط

- [ ] Advanced reporting with charts
- [ ] Barcode scanning integration
- [ ] Multi-language support (Arabic/English toggle)
- [ ] Mobile companion app
- [ ] Cloud backup integration

---

## 📖 Documentation / التوثيق

للمزيد من المعلومات:

- [Database Schema Details](docs/database.md) (To be created)
- [API Documentation](docs/api.md) (To be created)
- [User Guide](docs/user_guide.md) (To be created)

---

## 🤝 Contributing / المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

---

## 📄 License / الترخيص

This project is licensed under the MIT License.

---

## 👥 Authors / المؤلفون

- moshaban8com-bot

---

## 🙏 Acknowledgments / شكر وتقدير

- PySide6 (Qt for Python)
- SQLAlchemy ORM
- Alembic for migrations
- OpenPyXL for Excel handling

---

## 📞 Support / الدعم

للحصول على الدعم:
- فتح Issue على GitHub
- البريد الإلكتروني: support@example.com (placeholder)

---

<div dir="rtl">

## ملاحظات هامة

### قاعدة البيانات

- الافتراضي: SQLite محلية
- دعم PostgreSQL للإنتاج
- يتم إنشاء قاعدة البيانات تلقائياً عند أول تشغيل

### النسخ الاحتياطي

```bash
# Backup database (To be implemented in UI)
# النسخ الاحتياطي متاح من داخل النظام
```

### الأداء

- استخدام Indexes على الجداول الرئيسية
- Cache للأرصدة في جدول stock_balance
- Transaction atomicity أثناء الترحيل

</div>

---

**مع تحيات فريق التطوير** ❤️
