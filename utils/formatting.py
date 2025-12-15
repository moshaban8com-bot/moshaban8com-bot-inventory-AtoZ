"""
Number formatting utilities
دوال تنسيق الأرقام
"""

from decimal import Decimal
from typing import Optional


def format_number(value: Optional[Decimal], decimals: int = 2) -> str:
    """
    Format number with specified decimal places
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if value is None:
        return '0.00'
    
    return f'{value:,.{decimals}f}'


def format_quantity(qty: Optional[Decimal]) -> str:
    """Format quantity (4 decimal places)"""
    return format_number(qty, 4)


def format_currency(amount: Optional[Decimal]) -> str:
    """Format currency (2 decimal places)"""
    return format_number(amount, 2)


def parse_decimal(value: str) -> Optional[Decimal]:
    """Parse string to Decimal"""
    if not value:
        return None
    
    try:
        # Remove commas and convert
        clean_value = value.replace(',', '')
        return Decimal(clean_value)
    except Exception:
        return None
