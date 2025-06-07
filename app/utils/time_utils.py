"""
Time utilities for dynamic data calculations.
Provides date range calculations and growth rate analysis.
"""

from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
import calendar


def get_date_range(days: int) -> Tuple[datetime, datetime]:
    """Get start and end dates for a given number of days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate percentage between two values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)


def get_business_days_in_range(start_date: datetime, end_date: datetime) -> int:
    """Get number of business days in a date range."""
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def get_month_boundaries(date: datetime) -> Tuple[datetime, datetime]:
    """Get the first and last day of the month for a given date."""
    first_day = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = date.replace(
        day=calendar.monthrange(date.year, date.month)[1],
        hour=23, minute=59, second=59, microsecond=999999
    )
    return first_day, last_day


def get_quarter_boundaries(date: datetime) -> Tuple[datetime, datetime]:
    """Get the first and last day of the quarter for a given date."""
    quarter = (date.month - 1) // 3 + 1
    first_month = (quarter - 1) * 3 + 1
    last_month = quarter * 3
    
    first_day = date.replace(month=first_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = date.replace(
        month=last_month,
        day=calendar.monthrange(date.year, last_month)[1],
        hour=23, minute=59, second=59, microsecond=999999
    )
    return first_day, last_day


def get_year_boundaries(date: datetime) -> Tuple[datetime, datetime]:
    """Get the first and last day of the year for a given date."""
    first_day = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = date.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    return first_day, last_day


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_time_periods() -> Dict[str, int]:
    """Get common time periods in days."""
    return {
        "today": 1,
        "yesterday": 1,
        "last_7_days": 7,
        "last_30_days": 30,
        "last_90_days": 90,
        "last_6_months": 180,
        "last_year": 365
    }


def generate_time_series_data(
    start_date: datetime,
    end_date: datetime,
    base_value: float,
    growth_rate: float = 0.0,
    volatility: float = 0.1
) -> List[Dict[str, Any]]:
    """Generate time series data with growth trend and volatility."""
    import random
    
    data = []
    current_date = start_date
    days_total = (end_date - start_date).days
    
    while current_date <= end_date:
        days_elapsed = (current_date - start_date).days
        
        # Apply growth trend
        growth_factor = 1 + (growth_rate * (days_elapsed / days_total))
        
        # Apply volatility (random variation)
        volatility_factor = 1 + (random.uniform(-volatility, volatility))
        
        value = base_value * growth_factor * volatility_factor
        
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "value": round(value, 2),
            "timestamp": current_date.timestamp()
        })
        
        current_date += timedelta(days=1)
    
    return data


def get_period_comparison(current_period_days: int) -> Dict[str, Any]:
    """Get comparison periods for analytics."""
    end_date = datetime.now()
    current_start = end_date - timedelta(days=current_period_days)
    
    # Previous period (same duration)
    previous_end = current_start
    previous_start = previous_end - timedelta(days=current_period_days)
    
    # Year over year comparison
    yoy_end = end_date.replace(year=end_date.year - 1)
    yoy_start = current_start.replace(year=current_start.year - 1)
    
    return {
        "current": {
            "start": current_start,
            "end": end_date,
            "days": current_period_days
        },
        "previous": {
            "start": previous_start,
            "end": previous_end,
            "days": current_period_days
        },
        "year_over_year": {
            "start": yoy_start,
            "end": yoy_end,
            "days": current_period_days
        }
    } 