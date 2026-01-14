# Copilot Instructions for Dropout Newsletter RSS

## Project Overview

This is a Python-based RSS feed transformer that converts the Kill The Newsletter RSS feed (which aggregates Dropout newsletter content) into individual, organized RSS feeds for each show on the Dropout platform. The project runs automatically via GitHub Actions and deploys to GitHub Pages.

## Architecture

- **transform.py**: Main entry point that orchestrates the transformation process
- **src/fetcher.py**: Downloads RSS content from Kill The Newsletter
- **src/parser.py**: Parses RSS XML and extracts episode information, identifies shows
- **src/generator.py**: Creates valid RSS 2.0 feeds for each show
- **src/utils.py**: Utility functions for directory management, time conversion, and timezone handling
- **tests/**: Simple unit tests without pytest (uses plain Python assertions)

## Python Style and Conventions

### Code Style
- Use Python 3.8+ features (type hints are encouraged)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write clear docstrings in Google style format
- Keep functions focused and single-purpose

### Naming Conventions
- Use `snake_case` for functions and variables
- Use `PascalCase` for class names
- Use `UPPER_CASE` for constants
- Module names should be lowercase with underscores

### Import Organization
- Standard library imports first
- Third-party imports second
- Local application imports third
- Use `from typing import` for type hints

## Dependencies

The project uses minimal dependencies:
- **feedparser==6.0.10**: RSS/Atom feed parsing
- **python-dotenv==1.0.0**: Environment variable management
- **requests==2.31.0**: HTTP requests for fetching feeds

Avoid adding new dependencies unless absolutely necessary to keep the project lightweight. When updating dependencies, check for security vulnerabilities and update to patched versions as needed.

## Testing Approach

- Tests are in the `tests/` directory
- Tests use plain Python with simple assertions (no pytest framework)
- Each test function prints a success message using ✓ and ✅ emojis
- Tests are run directly with `python tests/test_*.py`
- Focus on testing core parsing, normalization, and transformation logic
- Tests should be simple and readable

### Running Tests
```bash
python tests/test_parser.py
python tests/test_real_feed.py
python tests/test_timezone.py
python tests/test_workflow.py
```

## Building and Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Run the transformer
python transform.py
```

### GitHub Actions Workflow
- The workflow runs every 6 hours (cron: '0 */6 * * *')
- Manual triggers via workflow_dispatch
- Uses secrets: `KILL_THE_NEWSLETTER_URL` (never expose in code or logs)
- Uses variables: `TIMEZONE_OFFSET`
- Deploys generated feeds to GitHub Pages
- Includes retry logic for transient failures
- Falls back to cached feeds if transformation fails

## Key Features to Preserve

1. **Privacy**: The Kill The Newsletter URL is stored as a GitHub secret and never exposed
2. **Timezone Conversion**: Support for converting ET times to user's local timezone
3. **Resilience**: Retry logic and fallback to cached feeds on failure
4. **Minimal Dependencies**: Keep the project lightweight and easy to maintain
5. **Valid RSS**: Generated feeds must be valid RSS 2.0 format

## RSS Feed Generation

- Feeds are stored in the `feeds/` directory (git-ignored, generated at runtime)
- Each show gets its own feed: `feeds/show-name.xml`
- An `all-shows.xml` feed combines all episodes
- An `index.html` page lists all available feeds
- Feed metadata includes proper last build date, language, and atom:link self-reference

## Common Tasks

### Adding Support for a New Show
1. The parser automatically detects shows from episode titles
2. Known show patterns are defined in `src/parser.py`
3. Show name normalization handles special characters and formats

### Modifying RSS Output
1. RSS generation logic is in `src/generator.py`
2. Use `xml.etree.ElementTree` for XML generation
3. Format dates using RFC 822 format for RSS compliance

### Adjusting Timezone Logic
1. Timezone conversion is in `src/utils.py`
2. Functions handle day-of-week adjustment when crossing midnight
3. Support both "7pm" and "1:30pm" time formats

## Environment Variables and Configuration

### Local Development (.env file)
- `KILL_THE_NEWSLETTER_URL`: RSS feed URL (required for local runs)
- `OUTPUT_DIR`: Directory for generated feeds (default: ./feeds, git-ignored)
- `TIMEZONE_OFFSET`: Hours offset from ET for timezone conversion (default: 0)

### GitHub Actions Configuration
- `KILL_THE_NEWSLETTER_URL`: Stored as a GitHub secret (never expose in code or logs)
- `TIMEZONE_OFFSET`: Stored as a GitHub Actions variable (can be configured per repository)
- Output directory is always `feeds/` in the workflow

## Security Considerations

- Never log or expose the `KILL_THE_NEWSLETTER_URL` secret
- Validate all external input from RSS feeds
- Use safe XML parsing (ElementTree, not eval or exec)
- Sanitize show names and episode titles before using in filenames

## Best Practices for This Project

1. **Keep changes minimal**: This is a focused tool with a specific purpose
2. **Maintain backward compatibility**: Existing feeds should continue to work
3. **Test with real data**: Use sample RSS feeds from `Samples/` directory when available
4. **Document time-related changes**: Timezone logic is complex, document edge cases
5. **Preserve the user experience**: Don't break GitHub Actions workflow or Pages deployment
6. **Write clear error messages**: Users primarily interact via GitHub Actions logs

## File Structure Conventions

- Keep source code in `src/` directory
- Keep tests in `tests/` directory
- Keep documentation in root directory (README.md, SETUP.md, IMPLEMENTATION.md)
- Configuration files in root (.env, requirements.txt)
- GitHub-specific files in `.github/` directory
