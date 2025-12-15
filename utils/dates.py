"""
Date and time utilities
دوال التاريخ والوقت
"""

from datetime import datetime, date
from typing import Optional
import calendar


def get_fiscal_year_dates(year: int, start_month: int = 1) -> tuple[date, date]:
    """
    Get fiscal year start and end dates
    
    Args:
        year: Year
        start_month: Starting month (1-12)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    start_date = date(year, start_month, 1)
    
    # Calculate end date (last day of the month before start month next year)
    if start_month == 1:
        end_year = year
        end_month = 12
    else:
        end_year = year + 1
        end_month = start_month - 1
    
    last_day = calendar.monthrange(end_year, end_month)[1]
    end_date = date(end_year, end_month, last_day)
    
    return start_date, end_date


def format_date_ar(dt: Optional[date]) -> str:
    """Format date in Arabic locale"""
    if not dt:
        return ''
    
    return dt.strftime('%Y-%m-%d')


def format_datetime_ar(dt: Optional[datetime]) -> str:
    """Format datetime in Arabic locale"""
    if not dt:
        return ''
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def parse_date(date_str: str) -> Optional[date]:
    """Parse date from string"""
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None
