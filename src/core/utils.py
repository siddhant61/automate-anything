"""
Utility functions for the OpenHPI automation platform.
"""

from datetime import datetime, timezone


def utcnow():
    """
    Return current UTC time as timezone-aware datetime.
    
    This replaces the deprecated datetime.utcnow() with a timezone-aware alternative.
    
    Returns:
        datetime: Current UTC time with timezone information
    """
    return datetime.now(timezone.utc)
