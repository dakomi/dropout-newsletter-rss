"""
Fetcher module for retrieving the Kill The Newsletter RSS feed
"""

import requests
from typing import Optional
import time


def fetch_feed(url: str, max_retries: int = 3, timeout: int = 30) -> Optional[str]:
    """
    Fetch the RSS feed content from the given URL with retry logic.
    
    Args:
        url: The Kill The Newsletter RSS feed URL
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        The raw RSS feed XML content as a string, or None if fetch fails
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            # Retry on transient errors (timeouts, connection, DNS, server errors)
            if attempt < max_retries:
                wait_time = 5 * attempt  # Linear backoff: 5s, 10s
                error_type = "Timeout" if isinstance(e, requests.exceptions.Timeout) else "Error"
                print(f"{error_type} on attempt {attempt}/{max_retries}: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error fetching feed from {url}: {e} (after {max_retries} attempts)")
                return None
