"""
Generator module for creating RSS feeds for each show
"""

from typing import List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .utils import format_description_with_day, get_env_variable


def generate_rss_feed(show_name: str, episodes: List[Dict[str, Any]], base_url: str = "", timezone_offset: int = 0) -> str:
    """
    Generate an RSS 2.0 feed for a specific show.
    
    Args:
        show_name: Name of the show (used in feed title)
        episodes: List of episode dictionaries for this show
        base_url: Base URL for the feed (optional)
        timezone_offset: Timezone offset from ET in hours (default: 0)
        
    Returns:
        RSS feed XML as a string
    """
    # Create RSS root element
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    # Create channel element
    channel = ET.SubElement(rss, 'channel')
    
    # Add channel metadata
    title = ET.SubElement(channel, 'title')
    title.text = format_show_title(show_name)
    
    description = ET.SubElement(channel, 'description')
    description.text = f"RSS feed for {format_show_title(show_name)} from Dropout"
    
    link = ET.SubElement(channel, 'link')
    link.text = base_url or 'https://www.dropout.tv/'
    
    language = ET.SubElement(channel, 'language')
    language.text = 'en-us'
    
    last_build_date = ET.SubElement(channel, 'lastBuildDate')
    last_build_date.text = format_rfc822_date(datetime.utcnow())
    
    # Add self-referencing atom link if base_url provided
    if base_url:
        atom_link = ET.SubElement(channel, 'atom:link')
        atom_link.set('href', f"{base_url}/feeds/{show_name}.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
    
    # Add episodes as items
    for episode in episodes:
        item = ET.SubElement(channel, 'item')
        
        item_title = ET.SubElement(item, 'title')
        item_title.text = episode.get('title', 'Untitled Episode')
        
        item_link = ET.SubElement(item, 'link')
        item_link.text = episode.get('link', '')
        
        item_description = ET.SubElement(item, 'description')
        # Format description with day and timezone conversion
        raw_description = episode.get('description', '')
        air_day = episode.get('air_day', None)
        formatted_description = format_description_with_day(raw_description, air_day, timezone_offset)
        item_description.text = formatted_description
        
        item_pub_date = ET.SubElement(item, 'pubDate')
        item_pub_date.text = episode.get('pub_date', format_rfc822_date(datetime.utcnow()))
        
        item_guid = ET.SubElement(item, 'guid')
        item_guid.text = episode.get('guid', episode.get('link', ''))
        item_guid.set('isPermaLink', 'false')
    
    # Convert to pretty-printed XML string
    xml_str = ET.tostring(rss, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    return '\n'.join(lines)


def generate_all_shows_feed(all_episodes: List[Dict[str, Any]], base_url: str = "", timezone_offset: int = 0) -> str:
    """
    Generate a combined RSS feed containing all shows.
    
    Args:
        all_episodes: List of all episode dictionaries
        base_url: Base URL for the feed (optional)
        timezone_offset: Timezone offset from ET in hours (default: 0)
        
    Returns:
        RSS feed XML as a string
    """
    # Create RSS root element
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    # Create channel element
    channel = ET.SubElement(rss, 'channel')
    
    # Add channel metadata
    title = ET.SubElement(channel, 'title')
    title.text = 'Dropout - All Shows'
    
    description = ET.SubElement(channel, 'description')
    description.text = 'Combined RSS feed for all Dropout shows'
    
    link = ET.SubElement(channel, 'link')
    link.text = base_url or 'https://www.dropout.tv/'
    
    language = ET.SubElement(channel, 'language')
    language.text = 'en-us'
    
    last_build_date = ET.SubElement(channel, 'lastBuildDate')
    last_build_date.text = format_rfc822_date(datetime.utcnow())
    
    # Add self-referencing atom link if base_url provided
    if base_url:
        atom_link = ET.SubElement(channel, 'atom:link')
        atom_link.set('href', f"{base_url}/feeds/all-shows.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
    
    # Sort episodes by date (newest first)
    sorted_episodes = sorted(
        all_episodes,
        key=lambda x: parse_date_safely(x.get('pub_date', '')),
        reverse=True
    )
    
    # Add episodes as items
    for episode in sorted_episodes:
        item = ET.SubElement(channel, 'item')
        
        item_title = ET.SubElement(item, 'title')
        item_title.text = episode.get('title', 'Untitled Episode')
        
        item_link = ET.SubElement(item, 'link')
        item_link.text = episode.get('link', '')
        
        item_description = ET.SubElement(item, 'description')
        # Format description with day and timezone conversion
        raw_description = episode.get('description', '')
        air_day = episode.get('air_day', None)
        formatted_description = format_description_with_day(raw_description, air_day, timezone_offset)
        item_description.text = formatted_description
        
        item_pub_date = ET.SubElement(item, 'pubDate')
        item_pub_date.text = episode.get('pub_date', format_rfc822_date(datetime.utcnow()))
        
        item_guid = ET.SubElement(item, 'guid')
        item_guid.text = episode.get('guid', episode.get('link', ''))
        item_guid.set('isPermaLink', 'false')
    
    # Convert to pretty-printed XML string
    xml_str = ET.tostring(rss, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    return '\n'.join(lines)


def format_show_title(show_name: str) -> str:
    """
    Format a show slug into a proper title.
    
    Args:
        show_name: Show name slug (e.g., 'dimension-20')
        
    Returns:
        Formatted title (e.g., 'Dimension 20')
    """
    # Split on hyphens and capitalize each word
    words = show_name.split('-')
    return ' '.join(word.capitalize() for word in words)


def format_rfc822_date(dt: datetime) -> str:
    """
    Format a datetime object as RFC 822 date string for RSS.
    
    Args:
        dt: datetime object
        
    Returns:
        RFC 822 formatted date string
    """
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')


def parse_date_safely(date_str: str) -> datetime:
    """
    Safely parse a date string, returning epoch if parsing fails.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object
    """
    if not date_str:
        return datetime(1970, 1, 1)
    
    try:
        # Try common RSS date formats
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except:
        return datetime(1970, 1, 1)
