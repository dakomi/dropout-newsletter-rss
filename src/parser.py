"""
Parser module for extracting episodes and identifying shows from the RSS feed
"""

import feedparser
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime
from html.parser import HTMLParser
import html as html_module


class ShowExtractor(HTMLParser):
    """HTML parser to extract show information from weekly newsletters."""
    
    def __init__(self):
        super().__init__()
        self.shows = []
        self.current_show = None
        self.current_day = None
        self.in_show_heading = False
        self.in_show_body = False
        self.in_schedule_header = False
        self.show_body_text = []
        self.capture_depth = 0
        self.schedule_header_depth = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Look for schedule header (day of week)
        if 'schedule-header__text' in attrs_dict.get('class', ''):
            self.in_schedule_header = True
            self.schedule_header_depth = 0
        
        # Look for show heading elements
        if attrs_dict.get('data-hs-cos-field') == 'show_info.show_heading':
            self.in_show_heading = True
            if self.current_show and self.current_show.get('title'):
                # Save previous show before starting a new one
                self.shows.append(self.current_show)
            self.current_show = {'title': '', 'description': '', 'day': self.current_day}
        # Look for show body elements
        elif attrs_dict.get('data-hs-cos-field') == 'show_info.show_body':
            self.in_show_body = True
            self.show_body_text = []
            self.capture_depth = 0
        elif self.in_show_body:
            self.capture_depth += 1
        
        if self.in_schedule_header:
            self.schedule_header_depth += 1
            
    def handle_endtag(self, tag):
        if self.in_schedule_header:
            self.schedule_header_depth -= 1
            if self.schedule_header_depth <= 0:
                self.in_schedule_header = False
                
        if self.in_show_heading:
            self.in_show_heading = False
        elif self.in_show_body:
            if self.capture_depth > 0:
                self.capture_depth -= 1
            else:
                # End of show body
                self.in_show_body = False
                if self.current_show and self.show_body_text:
                    self.current_show['description'] = ' '.join(self.show_body_text)
    
    def handle_data(self, data):
        if self.in_schedule_header:
            stripped = data.strip()
            if stripped and stripped in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                self.current_day = stripped
                
        if self.in_show_heading:
            self.current_show['title'] = data.strip()
        elif self.in_show_body and data.strip():
            self.show_body_text.append(data.strip())
    
    def get_shows(self):
        """Get all extracted shows, including the last one if not yet added."""
        if self.current_show and self.current_show.get('title'):
            if not self.shows or self.shows[-1] != self.current_show:
                self.shows.append(self.current_show)
        return self.shows


def is_confirmation_email(title: str) -> bool:
    """Check if this is a confirmation/setup email that should be ignored."""
    confirmation_keywords = [
        'please confirm',
        'confirm your mailbox',
        'kill-the-newsletter.com'
    ]
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in confirmation_keywords)


def is_weekly_newsletter(title: str, description: str) -> bool:
    """
    Detect if this is a weekly newsletter containing multiple shows.
    
    Weekly newsletters typically have:
    - "This week on Dropout" in the content
    - Multiple show headings in the HTML
    """
    # Minimum number of shows required to be considered a weekly newsletter
    MIN_SHOWS_FOR_NEWSLETTER = 2
    
    # Check for weekly newsletter indicators
    if 'this week on dropout' in description.lower():
        return True
    
    # Check if HTML contains multiple show headings
    if 'data-hs-cos-field="show_info.show_heading"' in description:
        # Count how many show headings are present
        count = description.count('data-hs-cos-field="show_info.show_heading"')
        return count >= MIN_SHOWS_FOR_NEWSLETTER
    
    return False


def extract_shows_from_newsletter(entry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract individual shows from a weekly newsletter email.
    
    Args:
        entry_data: Entry dictionary with title, description, link, etc.
        
    Returns:
        List of episode dictionaries, one per show
    """
    description = entry_data['description']
    
    # Parse HTML to extract shows
    parser = ShowExtractor()
    parser.feed(description)
    
    episodes = []
    for idx, show_info in enumerate(parser.get_shows()):
        show_title = show_info['title']
        show_desc = show_info.get('description', '')
        show_day = show_info.get('day', None)
        
        # Create unique GUID by combining original GUID with index and normalized name
        normalized_name = normalize_show_name(show_title)
        unique_guid = f"{entry_data['guid']}-{idx}-{normalized_name}"
        
        # Create an episode for this show
        episode = {
            'title': show_title,
            'description': show_desc,
            'link': entry_data['link'],
            'pub_date': entry_data['pub_date'],
            'guid': unique_guid,
            'show_name': extract_show_name(show_title),
            'air_day': show_day
        }
        episodes.append(episode)
    
    return episodes


def parse_episodes(feed_content: str) -> List[Dict[str, Any]]:
    """
    Parse RSS feed content and extract episodes with show information.
    
    Args:
        feed_content: Raw RSS feed XML content
        
    Returns:
        List of episode dictionaries with parsed information
    """
    # Use feedparser for basic parsing
    feed = feedparser.parse(feed_content)
    episodes = []
    
    # Also parse raw XML to get unescaped HTML content
    try:
        root = ET.fromstring(feed_content)
        # Handle both RSS and Atom feeds
        namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('.//atom:entry', namespaces)
        
        # Create a mapping of entry IDs to raw HTML content
        raw_content_map = {}
        for entry_elem in entries:
            entry_id = entry_elem.find('atom:id', namespaces)
            content_elem = entry_elem.find('atom:content', namespaces)
            if entry_id is not None and content_elem is not None:
                # Unescape HTML entities
                raw_html = html_module.unescape(content_elem.text or '')
                raw_content_map[entry_id.text] = raw_html
    except (ET.ParseError, AttributeError) as e:
        # If XML parsing fails, fall back to feedparser only
        raw_content_map = {}
    
    for entry in feed.entries:
        # Get raw HTML content if available
        entry_id = entry.get('id', '')
        description = raw_content_map.get(entry_id, '')
        
        # Fall back to feedparser's content if raw parsing failed
        if not description:
            if hasattr(entry, 'content') and entry.content:
                description = entry.content[0].get('value', '')
            if not description:
                description = entry.get('description', '') or entry.get('summary', '')
        
        entry_data = {
            'title': entry.get('title', ''),
            'description': description,
            'link': entry.get('link', ''),
            'pub_date': entry.get('published', '') or entry.get('updated', ''),
            'guid': entry.get('id', entry.get('link', '')),
        }
        
        # Skip confirmation emails
        if is_confirmation_email(entry_data['title']):
            continue
        
        # Check if this is a weekly newsletter with multiple shows
        if is_weekly_newsletter(entry_data['title'], entry_data['description']):
            # Extract individual shows from the newsletter
            newsletter_episodes = extract_shows_from_newsletter(entry_data)
            episodes.extend(newsletter_episodes)
        else:
            # Single show email - process normally
            episode = entry_data.copy()
            episode['show_name'] = extract_show_name(episode['title'])
            episodes.append(episode)
    
    return episodes


def extract_show_name(title: str) -> str:
    """
    Extract the show name from an episode title.
    
    Common patterns in Dropout newsletters:
    - "Show Name: Episode Title"
    - "Show Name - Episode Title"
    - "[Show Name] Episode Title"
    - "ALERT! ... Show Name ..." (alert-style titles)
    
    Args:
        title: Episode title from the RSS feed
        
    Returns:
        Normalized show name (lowercase, hyphenated)
    """
    # First, try to identify known shows anywhere in the title
    # This handles alert-style titles like "🚨PREMIERE ALERT! Watch Dimension 20: Gladlands NOW!"
    known_shows = {
        'dimension 20': 'dimension-20',
        'game changer': 'game-changer',
        'um actually': 'um-actually',
        'um, actually': 'um-actually',  # Handle comma variant
        'breaking news': 'breaking-news',
        'rats rent a shop': 'rats-rent-a-shop',
        'very important people': 'very-important-people',
        'make some noise': 'make-some-noise',
        'total forgiveness': 'total-forgiveness',
        'adventuring party': 'adventuring-party',
        'dirty laundry': 'dirty-laundry',
    }
    
    title_lower = title.lower()
    for show_key, show_slug in known_shows.items():
        if show_key in title_lower:
            return show_slug
    
    # If no known show found, try different patterns to extract show name
    patterns = [
        r'^([^:]+):\s*',      # "Show Name: Episode"
        r'^([^-]+)-\s*',      # "Show Name - Episode"
        r'^\[([^\]]+)\]\s*',  # "[Show Name] Episode"
        r'^([^|]+)\|\s*',     # "Show Name | Episode"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            show_name = match.group(1).strip()
            return normalize_show_name(show_name)
    
    # Default: use first part of title before any delimiter
    first_part = re.split(r'[:\-\|\[\]]', title)[0].strip()
    return normalize_show_name(first_part) if first_part else 'unknown-show'


def normalize_show_name(show_name: str) -> str:
    """
    Normalize show name to a URL-friendly slug.
    
    Args:
        show_name: Raw show name
        
    Returns:
        Normalized show name (lowercase, hyphenated)
    """
    # Convert to lowercase and replace spaces with hyphens
    normalized = show_name.lower().strip()
    # Remove special characters except hyphens and alphanumeric
    normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
    # Replace spaces with hyphens
    normalized = re.sub(r'\s+', '-', normalized)
    # Remove consecutive hyphens
    normalized = re.sub(r'-+', '-', normalized)
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    
    return normalized or 'unknown-show'


def group_episodes_by_show(episodes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group episodes by their show name.
    
    Args:
        episodes: List of episode dictionaries
        
    Returns:
        Dictionary mapping show names to lists of episodes
    """
    shows = {}
    
    for episode in episodes:
        show_name = episode.get('show_name', 'unknown-show')
        if show_name not in shows:
            shows[show_name] = []
        shows[show_name].append(episode)
    
    return shows
