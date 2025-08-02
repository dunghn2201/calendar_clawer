# Copilot Instructions for Lich Crawler Project

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Vietnamese Lunar Calendar data crawler project that extracts calendar information from multiple websites including lichviet.app, tuvi.vn, and lichvn.net.

## Development Guidelines
- Use modern Python practices with type hints
- Follow PEP 8 style guidelines
- Use async/await for web scraping when possible
- Handle exceptions gracefully with proper error logging
- Include Vietnamese comments for better understanding
- Use dataclasses for structured data
- Implement rate limiting to be respectful to target websites

## Key Technologies
- **Web Scraping**: BeautifulSoup4, Playwright, Selenium
- **Data Processing**: pandas, json, sqlite3
- **Scheduling**: schedule library
- **HTTP Requests**: requests, aiohttp
- **Logging**: Python logging module

## Code Style Preferences
- Use descriptive variable names in Vietnamese where appropriate
- Add docstrings for all functions and classes
- Use type hints consistently
- Prefer f-strings for string formatting
- Use pathlib for file operations

## Specific Instructions
- When scraping websites, always include User-Agent headers
- Implement retry logic for failed requests
- Save data in multiple formats (JSON, SQLite, CSV)
- Include data validation and cleaning functions
- Create separate modules for each website scraper
- Use configuration files for settings
