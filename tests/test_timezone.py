"""
Tests for timezone conversion and day extraction functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import (
    parse_time_string,
    convert_time_to_24h,
    convert_24h_to_time,
    adjust_day_for_offset,
    convert_et_time_description,
    format_description_with_day
)


def test_parse_time_string():
    """Test parsing time strings with and without minutes."""
    # With minutes
    result = parse_time_string("1:30pm")
    assert result == (1, 30, 'pm'), f"Expected (1, 30, 'pm'), got {result}"
    
    result = parse_time_string("10:30am")
    assert result == (10, 30, 'am'), f"Expected (10, 30, 'am'), got {result}"
    
    # Without minutes
    result = parse_time_string("7pm")
    assert result == (7, 0, 'pm'), f"Expected (7, 0, 'pm'), got {result}"
    
    result = parse_time_string("11am")
    assert result == (11, 0, 'am'), f"Expected (11, 0, 'am'), got {result}"
    
    print("✓ test_parse_time_string passed")


def test_convert_time_to_24h():
    """Test converting 12-hour time to minutes since midnight."""
    # AM times
    result = convert_time_to_24h(1, 30, 'am')
    assert result == 90, f"Expected 90, got {result}"  # 1:30am = 90 minutes
    
    result = convert_time_to_24h(12, 0, 'am')
    assert result == 0, f"Expected 0, got {result}"  # 12:00am = midnight
    
    # PM times
    result = convert_time_to_24h(1, 30, 'pm')
    assert result == 810, f"Expected 810, got {result}"  # 1:30pm = 13:30 = 810 minutes
    
    result = convert_time_to_24h(12, 0, 'pm')
    assert result == 720, f"Expected 720, got {result}"  # 12:00pm = noon = 720 minutes
    
    result = convert_time_to_24h(7, 0, 'pm')
    assert result == 1140, f"Expected 1140, got {result}"  # 7:00pm = 19:00 = 1140 minutes
    
    print("✓ test_convert_time_to_24h passed")


def test_convert_24h_to_time():
    """Test converting minutes since midnight to 12-hour time."""
    # Morning times
    result = convert_24h_to_time(90)
    assert result == (1, 30, 'am'), f"Expected (1, 30, 'am'), got {result}"
    
    result = convert_24h_to_time(0)
    assert result == (12, 0, 'am'), f"Expected (12, 0, 'am'), got {result}"
    
    # Afternoon/evening times
    result = convert_24h_to_time(810)
    assert result == (1, 30, 'pm'), f"Expected (1, 30, 'pm'), got {result}"
    
    result = convert_24h_to_time(720)
    assert result == (12, 0, 'pm'), f"Expected (12, 0, 'pm'), got {result}"
    
    result = convert_24h_to_time(1140)
    assert result == (7, 0, 'pm'), f"Expected (7, 0, 'pm'), got {result}"
    
    print("✓ test_convert_24h_to_time passed")


def test_adjust_day_for_offset():
    """Test adjusting day of week based on timezone offset."""
    # No day change
    result = adjust_day_for_offset("Friday", 5, "1:30pm")
    assert result == "Friday", f"Expected Friday, got {result}"
    
    # Forward day change (late night ET becomes next day)
    result = adjust_day_for_offset("Friday", 15, "11pm")
    assert result == "Saturday", f"Expected Saturday, got {result}"
    
    # Backward day change (early morning ET becomes previous day)
    result = adjust_day_for_offset("Monday", -10, "2am")
    assert result == "Sunday", f"Expected Sunday, got {result}"
    
    # Week wraparound
    result = adjust_day_for_offset("Sunday", 15, "11pm")
    assert result == "Monday", f"Expected Monday, got {result}"
    
    result = adjust_day_for_offset("Monday", -10, "2am")
    assert result == "Sunday", f"Expected Sunday, got {result}"
    
    print("✓ test_adjust_day_for_offset passed")


def test_convert_et_time_description():
    """Test converting ET times in descriptions to different timezones."""
    # No conversion (offset 0)
    desc = "7pm ET / 4pm PT Show description"
    result = convert_et_time_description(desc, 0)
    assert result == desc, f"Expected no change, got {result}"
    
    # Convert to AEST (+15 hours)
    desc = "7pm ET / 4pm PT Show description"
    result = convert_et_time_description(desc, 15)
    assert "10am" in result, f"Expected 10am in result, got {result}"
    assert "PT" not in result, f"Expected PT to be removed, got {result}"
    
    # Convert with minutes
    desc = "1:30pm ET / 10:30am PT Show description"
    result = convert_et_time_description(desc, 15)
    assert "4:30am" in result, f"Expected 4:30am in result, got {result}"
    
    # Convert to UK time (+5 hours)
    desc = "7pm ET / 4pm PT Show description"
    result = convert_et_time_description(desc, 5)
    assert "12am" in result or "midnight" in result.lower(), f"Expected midnight/12am in result, got {result}"
    
    print("✓ test_convert_et_time_description passed")


def test_format_description_with_day():
    """Test formatting descriptions with day and timezone."""
    # Add day without timezone conversion
    desc = "7pm ET / 4pm PT Show description"
    result = format_description_with_day(desc, "Thursday", 0)
    assert result.startswith("Thursday"), f"Expected to start with Thursday, got {result}"
    assert "7pm ET" in result, f"Expected 7pm ET in result, got {result}"
    
    # Add day with minutes
    desc = "1:30pm ET / 10:30am PT Show description"
    result = format_description_with_day(desc, "Friday", 0)
    assert result.startswith("Friday"), f"Expected to start with Friday, got {result}"
    assert "1:30pm ET" in result, f"Expected 1:30pm ET in result, got {result}"
    
    # Add day with timezone conversion
    desc = "7pm ET / 4pm PT Show description"
    result = format_description_with_day(desc, "Thursday", 15)
    assert result.startswith("Friday"), f"Expected day to change to Friday, got {result}"
    assert "10am" in result, f"Expected 10am in result, got {result}"
    
    # No day provided
    desc = "7pm ET / 4pm PT Show description"
    result = format_description_with_day(desc, None, 0)
    assert result == desc, f"Expected no change when no day provided, got {result}"
    
    # Description without time
    desc = "Just a regular description"
    result = format_description_with_day(desc, "Monday", 0)
    assert result == desc, f"Expected no change for description without time, got {result}"
    
    print("✓ test_format_description_with_day passed")


def test_timezone_examples():
    """Test realistic timezone conversion examples."""
    # AEST (UTC+10 or ET+15 during US DST)
    desc = "1:30pm ET / 10:30am PT The crew discusses the episode."
    result = format_description_with_day(desc, "Friday", 15)
    print(f"\nAEST Example:")
    print(f"  Input:  {desc}")
    print(f"  Output: {result}")
    assert "Saturday" in result
    assert "4:30am" in result
    
    # UK (UTC+0 or ET+5 during US DST)
    desc = "7pm ET / 4pm PT Evening show."
    result = format_description_with_day(desc, "Thursday", 5)
    print(f"\nUK Example:")
    print(f"  Input:  {desc}")
    print(f"  Output: {result}")
    assert "12am" in result or "midnight" in result.lower()
    
    # Japan (UTC+9 or ET+14 during US DST)
    desc = "11am ET / 8am PT Morning show."
    result = format_description_with_day(desc, "Monday", 14)
    print(f"\nJapan Example:")
    print(f"  Input:  {desc}")
    print(f"  Output: {result}")
    assert "Tuesday" in result
    assert "1am" in result
    
    print("\n✓ test_timezone_examples passed")


if __name__ == '__main__':
    print("Running timezone and day extraction tests...\n")
    print("=" * 60)
    
    test_parse_time_string()
    test_convert_time_to_24h()
    test_convert_24h_to_time()
    test_adjust_day_for_offset()
    test_convert_et_time_description()
    test_format_description_with_day()
    test_timezone_examples()
    
    print("\n" + "=" * 60)
    print("✅ All timezone tests passed!")
