"""
Configuration module for the Inventory Management System
نظام إدارة المخزون - ملف التكوين
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_CONFIG = {
    'default': 'sqlite',
    'sqlite': {
        'path': BASE_DIR / 'data' / 'inventory.db',
        'echo': False,  # Set to True for SQL logging
    },
    'postgresql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'inventory'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'echo': False,
    }
}

# Application settings
APP_CONFIG = {
    'name': 'نظام إدارة المخزون',
    'name_en': 'Inventory Management System',
    'version': '1.0.0',
    'rtl': True,  # Right-to-left layout
    'language': 'ar',  # Arabic
    'font_family': 'Cairo',
    'font_size': 10,
}

# Security settings
SECURITY_CONFIG = {
    'bcrypt_rounds': 12,
    'session_timeout': 3600,  # 1 hour in seconds
    'max_login_attempts': 5,
    'lockout_duration': 900,  # 15 minutes in seconds
}

# Excel/CSV settings
EXCEL_CONFIG = {
    'max_import_rows': 10000,
    'csv_encoding': 'utf-8-sig',  # UTF-8 with BOM
    'export_formats': ['xlsx', 'csv'],
    'templates_dir': BASE_DIR / 'import_export' / 'templates',
}

# Costing settings
COSTING_CONFIG = {
    'default_method': 'average',  # Average costing
    'precision': 4,  # Decimal places for costs
}

# Document settings
DOCUMENT_CONFIG = {
    'lock_posted': True,  # Lock posted documents by default
    'require_approval': False,  # Approval workflow disabled by default
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'file': BASE_DIR / 'logs' / 'inventory.log',
    'max_bytes': 10485760,  # 10 MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Resources paths
RESOURCES_CONFIG = {
    'icons_dir': BASE_DIR / 'resources' / 'icons',
    'fonts_dir': BASE_DIR / 'resources' / 'fonts',
    'styles_dir': BASE_DIR / 'resources' / 'styles',
}

# Backup settings
BACKUP_CONFIG = {
    'backup_dir': BASE_DIR / 'backups',
    'auto_backup': True,
    'backup_retention_days': 30,
}


def get_database_url(db_type='default'):
    """Get database URL for SQLAlchemy"""
    if db_type == 'default':
        db_type = DATABASE_CONFIG['default']
    
    if db_type == 'sqlite':
        db_path = DATABASE_CONFIG['sqlite']['path']
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"
    elif db_type == 'postgresql':
        pg_config = DATABASE_CONFIG['postgresql']
        return (f"postgresql://{pg_config['user']}:{pg_config['password']}"
                f"@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}")
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        BASE_DIR / 'data',
        BASE_DIR / 'logs',
        EXCEL_CONFIG['templates_dir'],
        BACKUP_CONFIG['backup_dir'],
        RESOURCES_CONFIG['icons_dir'],
        RESOURCES_CONFIG['fonts_dir'],
        RESOURCES_CONFIG['styles_dir'],
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
ensure_directories()
