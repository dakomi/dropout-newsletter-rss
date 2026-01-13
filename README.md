# Dropout Newsletter RSS Transformer

A tool for transforming the **Kill The Newsletter** RSS feed into per-show RSS feeds for Dropout content.

## Overview

This project takes the Kill The Newsletter RSS feed (which aggregates Dropout newsletter content) and transforms it into individual, organized RSS feeds for each show on the Dropout platform. This allows you to subscribe to specific shows without having to parse through a general newsletter feed.

## Purpose

**Kill The Newsletter** converts email newsletters into RSS feeds. However, the Dropout newsletter is a single combined feed containing content from multiple shows. This transformer solves that problem by:

- Parsing the Kill The Newsletter RSS feed
- Identifying individual shows and episodes
- Creating separate RSS feeds for each show
- Maintaining chronological order and metadata
- Allowing selective subscription to shows of interest

## Features

- 📺 **Per-Show RSS Feeds**: Generate individual feeds for each Dropout show
- 🔄 **Automatic Updates**: Continuously sync with the Kill The Newsletter feed (hourly via GitHub Actions)
- 📋 **Complete Metadata**: Preserve episode information, descriptions, and dates
- 🎯 **Selective Subscription**: Subscribe only to shows you want to follow
- 🚀 **Simple Setup**: Easy to configure and deploy with GitHub Actions
- 🔒 **Privacy**: Source feed URL stored securely as a GitHub secret (not publicly visible)

## How It Works

### Step 1: Get Your Kill The Newsletter URL

1. Visit [Kill The Newsletter](https://www.killTheNewsletter.com/)
2. Enter the Dropout newsletter email address
3. Receive your Kill The Newsletter RSS feed URL

### Step 2: Configure the Transformer

The transformer reads the Kill The Newsletter RSS feed and parses each episode to identify:
- Episode title and show name
- Publication date
- Episode description/summary
- Content details

### Step 3: Generate Per-Show Feeds

The tool creates individual RSS feeds organized by show:
- `feeds/show-name.xml` - Individual show feeds
- `feeds/all-shows.xml` - Combined feed (optional)

### Step 4: Subscribe

Use your preferred RSS reader to subscribe to:
- Individual show feeds: `https://your-domain/feeds/show-name.xml`
- All shows feed: `https://your-domain/feeds/all-shows.xml`

## Quick Start with GitHub Actions (Recommended)

The easiest way to use this project is with the included GitHub Actions workflow:

1. **Fork this repository** to your GitHub account
2. **Configure GitHub Pages**:
   - Go to Settings → Pages
   - Set Source to "GitHub Actions"
3. **Add your feed URL as a secret**:
   - Go to Settings → Secrets and variables → Actions
   - Create a new secret named `KILL_THE_NEWSLETTER_URL`
   - Paste your Kill The Newsletter feed URL as the value
4. **Trigger the workflow**:
   - Go to Actions → Update RSS Feeds → Run workflow
5. **Access your feeds** at `https://[username].github.io/[repo-name]/`

📖 **Detailed setup instructions**: See [SETUP.md](SETUP.md)

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/dakomi/dropout-newsletter-rss.git
cd dropout-newsletter-rss

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Kill The Newsletter RSS feed URL
KILL_THE_NEWSLETTER_URL=https://www.killTheNewsletter.com/feeds/xxxxx.xml

# Output directory for generated feeds
OUTPUT_DIR=./feeds

# Update frequency (in minutes)
UPDATE_INTERVAL=60
```

## Usage

### Run the Transformer

```bash
# Single run
python transform.py

# Continuous mode (updates at specified interval)
python transform.py --watch
```

### Output

The generated feeds will be saved in the configured `OUTPUT_DIR`:

```
feeds/
├── all-shows.xml              # Combined feed for all shows
├── breaking-news.xml
├── dimension-20.xml
├── game-changer.xml
├── rats-rent-a-shop.xml
├── um-actually.xml
└── ... (one file per show)
```

Each feed is a valid RSS 2.0 feed that can be imported into any RSS reader.

## Project Structure

```
dropout-newsletter-rss/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment configuration
├── transform.py              # Main transformation script
├── src/
│   ├── __init__.py
│   ├── fetcher.py            # Kill The Newsletter feed fetcher
│   ├── parser.py             # RSS parsing and episode extraction
│   ├── generator.py          # Per-show feed generation
│   └── utils.py              # Utility functions
├── feeds/                    # Output directory (generated)
└── tests/                    # Unit tests
```

## API Reference

### Main Functions

#### `transform_feed(kill_the_newsletter_url)`

Fetches the Kill The Newsletter RSS and generates per-show feeds.

**Parameters:**
- `kill_the_newsletter_url` (str): URL to the Kill The Newsletter feed

**Returns:**
- `dict`: Dictionary mapping show names to feed content

**Example:**
```python
from src.fetcher import transform_feed

feeds = transform_feed('https://www.killTheNewsletter.com/feeds/xxxxx.xml')
for show_name, feed_content in feeds.items():
    print(f"Generated feed for {show_name}")
```

#### `parse_episodes(feed_content)`

Parses RSS feed content and extracts episodes.

**Parameters:**
- `feed_content` (str): Raw RSS feed XML content

**Returns:**
- `list`: List of episode dictionaries

## Show Categories

This transformer recognizes and organizes the following Dropout shows:

- **Breaking News**
- **Dimension 20** (D&D and ttrpg content)
- **Game Changer** (Comedy games)
- **Rats Rent a Shop**
- **Um, Actually?** (Comedy trivia)
- ... and more as added to the Dropout newsletter

## Troubleshooting

### No Shows Detected

If the transformer isn't detecting shows:

1. Verify the Kill The Newsletter URL is correct
2. Check that the Dropout newsletter is being sent to the email
3. Ensure the Kill The Newsletter feed has updated content

### Feeds Not Updating

If feeds haven't been updated recently:

1. Check the `UPDATE_INTERVAL` setting
2. Review logs for any errors
3. Verify internet connectivity

### RSS Reader Issues

If feeds aren't importing correctly:

1. Validate the feed URLs are accessible
2. Try a different RSS reader
3. Check the feed XML for validation errors using an [RSS Validator](https://www.feedvalidator.org/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with linting
flake8 src/
```

## Limitations

- Depends on Kill The Newsletter's continued operation
- Updates are limited by Kill The Newsletter's refresh rate
- Requires the Dropout newsletter to be sent to the Kill The Newsletter email
- Per-show detection relies on consistent episode naming in the newsletter

## Related Projects

- [Kill The Newsletter](https://www.killTheNewsletter.com/) - Email to RSS converter
- [Dropout](https://www.dropout.tv/) - Official Dropout content platform
- [RSS Standards](https://www.rssboard.org/rss-specification) - RSS 2.0 Specification

## License

This project is provided as-is for personal use. Please respect Dropout's content rights and terms of service.

## Disclaimer

This is an unofficial tool created by fans for personal use. It is not affiliated with or endorsed by Dimension 20, Dropout, or their parent companies. Please support the creators by watching content on the official Dropout platform when possible.

## Support

For issues, questions, or suggestions:

1. Check existing [Issues](https://github.com/dakomi/dropout-newsletter-rss/issues)
2. Create a new issue with a detailed description
3. Include relevant logs or error messages

## Changelog

### Version 1.0.0 (2026-01-12)
- Initial release
- Per-show RSS feed generation
- Support for major Dropout shows
- Continuous update mode
- Comprehensive documentation

---

**Last Updated**: 2026-01-12

Made with ❤️ for Dropout fans
