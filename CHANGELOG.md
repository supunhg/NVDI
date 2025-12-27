# Changelog

All notable changes to nvdi will be documented in this file.

## [1.0.0] - 2025-12-27

### Added
- Initial release of nvdi (NVD CLI)
- NVD API 2.0 integration with async operations
- SQLite database for local CVE storage and offline queries
- Disk-based caching for API responses
- Rich terminal UI with color-coded CVSS severity
- CVE retrieval with basic, full, and field-selection modes
- Keyword search with CVSS score filtering
- Product monitoring system
- Multi-format export (JSON, CSV, YAML, TXT)
- Database management commands (info, clear)
- Statistics dashboard
- Comprehensive test suite (39 tests)
- PyInstaller binary packaging
- Virtual environment isolation

### Features
- **Get CVE**: Retrieve CVE data with `--full` or `--fields` options
- **Search**: Keyword search with `--min-score` and `--max-score` filters
- **Export**: Export CVE data to JSON, CSV, YAML, or TXT formats
- **Monitor**: Track products for new vulnerabilities
- **Database**: SQLite storage with reset and info commands
- **Stats**: View vulnerability statistics and trends
- **Caching**: Smart caching reduces API calls and improves performance

### Technical Details
- Python 3.8+ with async/await patterns
- Typer CLI framework with Rich terminal output
- httpx for async HTTP requests
- Pydantic 2.x for data validation
- aiosqlite for async database operations
- diskcache for HTTP response caching
- Full NVD API 2.0 data extraction (CVSS v2/v3, references, weaknesses, CPE configs)

### Documentation
- Comprehensive README with usage examples
- ARCHITECTURE document with design details
- MIT License
- Environment configuration template (.env.example)
- Automated setup script (setup.sh)
- Automated test script (test.sh)
- Binary build script (build.sh)

### Repository
- GitHub layout with proper .gitignore
- Author: Supun Hewagamage (@supunhg)
- License: MIT
