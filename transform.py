#!/usr/bin/env python3
"""
Main script for transforming Kill The Newsletter feed into per-show RSS feeds.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.fetcher import fetch_feed
from src.parser import parse_episodes, group_episodes_by_show
from src.generator import generate_rss_feed, generate_all_shows_feed
from src.utils import ensure_directory, get_env_variable


def transform_feed(kill_the_newsletter_url: str, output_dir: str = './feeds', base_url: str = "", timezone_offset: int = 0) -> dict:
    """
    Main transformation function that fetches, parses, and generates feeds.
    
    Args:
        kill_the_newsletter_url: URL to the Kill The Newsletter feed
        output_dir: Directory to save generated feeds
        base_url: Base URL for feed self-references
        timezone_offset: Timezone offset from ET in hours (default: 0)
        
    Returns:
        Dictionary mapping show names to feed file paths
    """
    print(f"Fetching feed from Kill The Newsletter...")
    feed_content = fetch_feed(kill_the_newsletter_url)
    
    if not feed_content:
        print("Error: Failed to fetch feed content")
        return {}
    
    print("Parsing episodes...")
    episodes = parse_episodes(feed_content)
    
    if not episodes:
        print("Warning: No episodes found in feed")
        return {}
    
    print(f"Found {len(episodes)} episode(s)")
    
    # Group episodes by show
    shows = group_episodes_by_show(episodes)
    print(f"Identified {len(shows)} show(s): {', '.join(shows.keys())}")
    
    # Ensure output directory exists
    ensure_directory(output_dir)
    
    # Generate per-show feeds
    feed_files = {}
    for show_name, show_episodes in shows.items():
        print(f"Generating feed for {show_name} ({len(show_episodes)} episode(s))...")
        feed_xml = generate_rss_feed(show_name, show_episodes, base_url, timezone_offset)
        
        # Write feed to file
        feed_path = Path(output_dir) / f"{show_name}.xml"
        with open(feed_path, 'w', encoding='utf-8') as f:
            f.write(feed_xml)
        
        feed_files[show_name] = str(feed_path)
        print(f"  ✓ Saved to {feed_path}")
    
    # Generate combined all-shows feed
    print("Generating combined all-shows feed...")
    all_shows_xml = generate_all_shows_feed(episodes, base_url, timezone_offset)
    all_shows_path = Path(output_dir) / "all-shows.xml"
    with open(all_shows_path, 'w', encoding='utf-8') as f:
        f.write(all_shows_xml)
    feed_files['all-shows'] = str(all_shows_path)
    print(f"  ✓ Saved to {all_shows_path}")
    
    print("\n✅ Feed transformation complete!")
    print(f"Generated {len(feed_files)} feed(s) in {output_dir}/")
    
    return feed_files


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Transform Kill The Newsletter feed into per-show RSS feeds'
    )
    parser.add_argument(
        '--url',
        help='Kill The Newsletter feed URL (overrides KILL_THE_NEWSLETTER_URL env var)'
    )
    parser.add_argument(
        '--output',
        help='Output directory for feeds (overrides OUTPUT_DIR env var)',
        default=None
    )
    parser.add_argument(
        '--base-url',
        help='Base URL for feed self-references',
        default=''
    )
    parser.add_argument(
        '--timezone-offset',
        type=int,
        help='Timezone offset from ET in hours (overrides TIMEZONE_OFFSET env var)',
        default=None
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Continuous mode - not implemented yet'
    )
    
    args = parser.parse_args()
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Get configuration from args or environment
    feed_url = args.url or get_env_variable('KILL_THE_NEWSLETTER_URL')
    output_dir = args.output or get_env_variable('OUTPUT_DIR', './feeds')
    base_url = args.base_url or get_env_variable('BASE_URL', '')
    
    # Get timezone offset (default to 0 if not specified)
    if args.timezone_offset is not None:
        timezone_offset = args.timezone_offset
    else:
        timezone_offset_str = get_env_variable('TIMEZONE_OFFSET', '0')
        try:
            timezone_offset = int(timezone_offset_str)
        except ValueError:
            print(f"Warning: Invalid TIMEZONE_OFFSET value '{timezone_offset_str}', using 0")
            timezone_offset = 0
    
    if not feed_url:
        print("Error: No Kill The Newsletter URL provided!")
        print("Please set KILL_THE_NEWSLETTER_URL environment variable or use --url argument")
        sys.exit(1)
    
    if args.watch:
        print("Error: Watch mode not implemented yet")
        sys.exit(1)
    
    # Run transformation
    transform_feed(feed_url, output_dir, base_url, timezone_offset)


if __name__ == '__main__':
    main()
