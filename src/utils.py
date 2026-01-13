"""
Utility functions for the transformer
"""

import os
import re
from pathlib import Path
from typing import Tuple, Optional


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_env_variable(var_name: str, default: str = "") -> str:
    """
    Get an environment variable with a default value.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not set
        
    Returns:
        Value of the environment variable or default
    """
    return os.getenv(var_name, default)


def parse_time_string(time_str: str) -> Optional[Tuple[int, int, str]]:
    """
    Parse a time string like "1:30pm" or "7pm" into hours, minutes, and period.
    
    Args:
        time_str: Time string (e.g., "1:30pm", "10:30am", "7pm")
        
    Returns:
        Tuple of (hours, minutes, period) or None if parsing fails
    """
    # First try with minutes
    match = re.match(r'(\d+):(\d+)(am|pm)', time_str.lower().strip())
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        period = match.group(3)
        return (hours, minutes, period)
    
    # Try without minutes (e.g., "7pm")
    match = re.match(r'(\d+)(am|pm)', time_str.lower().strip())
    if match:
        hours = int(match.group(1))
        minutes = 0
        period = match.group(2)
        return (hours, minutes, period)
    
    return None


def convert_time_to_24h(hours: int, minutes: int, period: str) -> int:
    """
    Convert 12-hour time to total minutes since midnight.
    
    Args:
        hours: Hour (1-12)
        minutes: Minutes (0-59)
        period: 'am' or 'pm'
        
    Returns:
        Total minutes since midnight
    """
    if period == 'pm' and hours != 12:
        hours += 12
    elif period == 'am' and hours == 12:
        hours = 0
    return hours * 60 + minutes


def convert_24h_to_time(total_minutes: int) -> Tuple[int, int, str]:
    """
    Convert total minutes since midnight to 12-hour time.
    
    Args:
        total_minutes: Total minutes since midnight
        
    Returns:
        Tuple of (hours, minutes, period)
    """
    # Handle day overflow/underflow
    total_minutes = total_minutes % (24 * 60)
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    if hours == 0:
        return (12, minutes, 'am')
    elif hours < 12:
        return (hours, minutes, 'am')
    elif hours == 12:
        return (12, minutes, 'pm')
    else:
        return (hours - 12, minutes, 'pm')


def adjust_day_for_offset(day: str, hour_offset: int, original_time_str: str) -> str:
    """
    Adjust the day of the week based on timezone offset.
    
    Args:
        day: Original day of the week
        hour_offset: Timezone offset in hours (can be negative or positive)
        original_time_str: Original time string or description containing time (e.g., "7pm ET" or "7pm ET / 4pm PT Description")
        
    Returns:
        Adjusted day of the week
    """
    if not day:
        return day
    
    # Extract just the time portion from the string if it contains ET time
    import re
    time_match = re.search(r'(\d+(?::\d+)?(?:am|pm))\s*ET', original_time_str, re.IGNORECASE)
    if time_match:
        time_str = time_match.group(1)
    else:
        # Fall back to parsing the whole string
        time_str = original_time_str
    
    # Parse the original time
    parsed = parse_time_string(time_str)
    if not parsed:
        return day
    
    hours, minutes, period = parsed
    original_minutes = convert_time_to_24h(hours, minutes, period)
    adjusted_minutes = original_minutes + (hour_offset * 60)
    
    # Check if we crossed midnight
    days_offset = 0
    if adjusted_minutes < 0:
        days_offset = -1
    elif adjusted_minutes >= 24 * 60:
        days_offset = 1
    
    if days_offset == 0:
        return day
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    try:
        current_index = days_of_week.index(day)
        new_index = (current_index + days_offset) % 7
        return days_of_week[new_index]
    except ValueError:
        return day


def convert_et_time_description(description: str, timezone_offset: int) -> str:
    """
    Convert ET times in a description to a different timezone.
    
    Args:
        description: Description containing times like "1:30pm ET / 10:30am PT" or "7pm ET / 4pm PT"
        timezone_offset: Offset from ET in hours (e.g., +15 for AEST)
        
    Returns:
        Updated description with converted times
    """
    if timezone_offset == 0:
        return description
    
    # Match patterns like "1:30pm ET", "7pm ET" (with or without minutes)
    et_pattern = r'(\d+(?::\d+)?(?:am|pm))\s*ET'
    
    def replace_time(match):
        et_time = match.group(1)
        parsed = parse_time_string(et_time)
        if not parsed:
            return match.group(0)
        
        hours, minutes, period = parsed
        et_minutes = convert_time_to_24h(hours, minutes, period)
        new_minutes = et_minutes + (timezone_offset * 60)
        new_hours, new_mins, new_period = convert_24h_to_time(new_minutes)
        
        # Format with or without minutes
        if new_mins == 0:
            return f"{new_hours}{new_period}"
        else:
            return f"{new_hours}:{new_mins:02d}{new_period}"
    
    # Replace all ET times
    result = re.sub(et_pattern, replace_time, description, flags=re.IGNORECASE)
    
    # Remove PT time if it exists (since we're converting from ET)
    result = re.sub(r'\s*/\s*\d+(?::\d+)?(?:am|pm)\s*PT', '', result, flags=re.IGNORECASE)
    
    return result


def format_description_with_day(description: str, air_day: Optional[str], timezone_offset: int = 0) -> str:
    """
    Format the description to include the air day and optionally convert timezone.
    
    Args:
        description: Original description (e.g., "1:30pm ET / 10:30am PT Episode description" or "7pm ET / 4pm PT Episode description")
        air_day: Day of the week (e.g., "Friday")
        timezone_offset: Timezone offset from ET in hours (0 for no conversion)
        
    Returns:
        Formatted description with day and converted time
    """
    if not description:
        return description
    
    # Check if there's a time pattern in the description (with or without minutes)
    time_pattern = r'\d+(?::\d+)?(?:am|pm)\s*ET'
    has_time = re.search(time_pattern, description, re.IGNORECASE)
    
    if not has_time:
        return description
    
    # Convert timezone if needed
    converted_desc = description
    adjusted_day = air_day
    
    if timezone_offset != 0:
        # Adjust the day if timezone crosses midnight
        if air_day:
            adjusted_day = adjust_day_for_offset(air_day, timezone_offset, description)
        converted_desc = convert_et_time_description(description, timezone_offset)
    
    # Prepend day to the description if we have one
    if adjusted_day:
        return f"{adjusted_day} {converted_desc}"
    else:
        return converted_desc

