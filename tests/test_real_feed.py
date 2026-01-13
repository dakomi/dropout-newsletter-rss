"""
Test the parser with the real RSS feed sample from the Samples directory
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser import parse_episodes, group_episodes_by_show
from src.generator import generate_rss_feed, generate_all_shows_feed


def test_parse_real_rss_feed():
    """Test parsing the real RSS feed sample."""
    print("Testing with real RSS feed sample...")
    
    # Load the real RSS feed sample
    samples_dir = Path(__file__).parent.parent / 'Samples'
    feed_file = samples_dir / 'Dropout kill-the-newsletter.xml'
    
    assert feed_file.exists(), f"Sample feed file not found: {feed_file}"
    
    with open(feed_file, 'r', encoding='utf-8') as f:
        feed_content = f.read()
    
    # Parse episodes
    episodes = parse_episodes(feed_content)
    print(f"✓ Parsed {len(episodes)} episodes from real feed")
    
    # Should have found some episodes
    assert len(episodes) > 0, "No episodes found in real feed"
    
    # Check that episodes have required fields
    for episode in episodes:
        assert 'title' in episode, "Episode missing title"
        assert 'show_name' in episode, "Episode missing show_name"
        assert 'pub_date' in episode, "Episode missing pub_date"
        assert 'link' in episode, "Episode missing link"
        assert 'guid' in episode, "Episode missing guid"
    
    print(f"✓ All {len(episodes)} episodes have required fields")
    
    # Display parsed episodes
    print("\nParsed episodes:")
    for i, ep in enumerate(episodes, 1):
        print(f"  {i}. {ep['title']}")
        print(f"     Show: {ep['show_name']}")
        print(f"     Date: {ep['pub_date']}")
    
    return episodes


def test_group_real_episodes():
    """Test grouping episodes from real feed by show."""
    print("\nTesting episode grouping...")
    
    # Get episodes from previous test
    samples_dir = Path(__file__).parent.parent / 'Samples'
    feed_file = samples_dir / 'Dropout kill-the-newsletter.xml'
    
    with open(feed_file, 'r', encoding='utf-8') as f:
        feed_content = f.read()
    
    episodes = parse_episodes(feed_content)
    
    # Group by show
    shows = group_episodes_by_show(episodes)
    print(f"✓ Grouped into {len(shows)} show(s)")
    
    # Display shows
    print("\nShows found:")
    for show_name, show_episodes in shows.items():
        print(f"  - {show_name}: {len(show_episodes)} episode(s)")
    
    assert len(shows) > 0, "No shows found after grouping"
    
    return shows


def test_generate_feeds_from_real_data():
    """Test generating RSS feeds from real feed data."""
    print("\nTesting feed generation...")
    
    # Load and parse real feed
    samples_dir = Path(__file__).parent.parent / 'Samples'
    feed_file = samples_dir / 'Dropout kill-the-newsletter.xml'
    
    with open(feed_file, 'r', encoding='utf-8') as f:
        feed_content = f.read()
    
    episodes = parse_episodes(feed_content)
    shows = group_episodes_by_show(episodes)
    
    # Generate feed for each show
    for show_name, show_episodes in shows.items():
        feed_xml = generate_rss_feed(show_name, show_episodes)
        assert len(feed_xml) > 0, f"Generated empty feed for {show_name}"
        assert '<?xml' in feed_xml, f"Feed for {show_name} missing XML declaration"
        assert '<rss' in feed_xml, f"Feed for {show_name} missing RSS tag"
        print(f"✓ Generated feed for {show_name} ({len(feed_xml)} chars)")
    
    # Generate all-shows feed
    all_shows_xml = generate_all_shows_feed(episodes)
    assert len(all_shows_xml) > 0, "Generated empty all-shows feed"
    assert '<?xml' in all_shows_xml, "All-shows feed missing XML declaration"
    assert '<rss' in all_shows_xml, "All-shows feed missing RSS tag"
    print(f"✓ Generated all-shows feed ({len(all_shows_xml)} chars)")
    
    # Optionally write to test output directory
    output_dir = Path('/tmp/test-real-feed-output')
    output_dir.mkdir(exist_ok=True)
    
    for show_name, show_episodes in shows.items():
        feed_xml = generate_rss_feed(show_name, show_episodes)
        output_file = output_dir / f"{show_name}.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(feed_xml)
        print(f"  Wrote {output_file}")
    
    all_shows_file = output_dir / "all-shows.xml"
    with open(all_shows_file, 'w', encoding='utf-8') as f:
        f.write(all_shows_xml)
    print(f"  Wrote {all_shows_file}")
    
    print(f"\n✓ Test feeds written to {output_dir}")


if __name__ == '__main__':
    print("Running tests with real RSS feed sample...\n")
    print("=" * 60)
    
    episodes = test_parse_real_rss_feed()
    shows = test_group_real_episodes()
    test_generate_feeds_from_real_data()
    
    print("\n" + "=" * 60)
    print("✅ All real feed tests passed!")
