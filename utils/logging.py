"""
Utility functions for the inventory system
دوال مساعدة
"""

import logging
from pathlib import Path
from config import LOGGING_CONFIG


def setup_logging():
    """Setup logging configuration"""
    log_file = LOGGING_CONFIG['file']
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=LOGGING_CONFIG['level'],
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('inventory')


def get_logger(name: str):
    """Get a logger for a module"""
    return logging.getLogger(f'inventory.{name}')
