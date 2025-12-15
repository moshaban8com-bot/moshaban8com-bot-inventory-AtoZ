"""
Database base configuration and session management
قاعدة البيانات - إعدادات أساسية
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from config import get_database_url, DATABASE_CONFIG

# Create base class for models
Base = declarative_base()

# Global engine and session factory
_engine = None
_session_factory = None


def init_db(db_type='default', echo=False):
    """Initialize database engine and session factory"""
    global _engine, _session_factory
    
    db_url = get_database_url(db_type)
    
    # Get echo setting from config if not specified
    if db_type == 'default':
        db_type = DATABASE_CONFIG['default']
    echo = echo or DATABASE_CONFIG.get(db_type, {}).get('echo', False)
    
    _engine = create_engine(db_url, echo=echo)
    _session_factory = scoped_session(sessionmaker(bind=_engine))
    
    return _engine


def get_engine():
    """Get the database engine"""
    if _engine is None:
        init_db()
    return _engine


def get_session():
    """Get a new database session"""
    if _session_factory is None:
        init_db()
    return _session_factory()


@contextmanager
def session_scope():
    """Provide a transactional scope for database operations"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables():
    """Create all database tables"""
    # Import all models to register them with Base.metadata
    # Import here to avoid circular dependency at module level
    from data import models, documents, security, policies
    Base.metadata.create_all(get_engine())


def drop_all_tables():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(get_engine())
