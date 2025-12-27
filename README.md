# nvdi

**NVD CLI** - Command-line tool for searching, monitoring, and analyzing CVE data from the National Vulnerability Database.

**Author:** Supun Hewagamage ([@supunhg](https://github.com/supunhg))  
**License:** MIT

## Features

- 🔍 Search CVEs by keyword with CVSS filtering
- 📊 Local SQLite database for offline queries
- 📈 Statistical analysis of vulnerability trends
- 👀 Monitor products for new CVEs
- 💾 Export CVE data (JSON, CSV, YAML, TXT)
- ⚡ Smart caching for performance
- 🎨 Rich terminal output with color-coded severity
- 🔧 Flexible field selection and full data extraction

## Installation

### Option 1: Binary (Recommended)

Download the pre-built binary from [releases](https://github.com/supunhg/nvdi/releases) or build it yourself:

```bash
./build.sh
sudo cp dist/nvdi /usr/local/bin/
```

The binary includes Python runtime and all dependencies - no installation required.

### Option 2: From Source

```bash
./setup.sh
source .venv/bin/activate
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### Get CVE Information
```bash
# Basic info
nvdi get cve CVE-2021-44228

# Full comprehensive data
nvdi get cve CVE-2021-44228 --full

# Specific fields only
nvdi get cve CVE-2021-44228 --fields "id,cvssv3,references"
```

### Search CVEs
```bash
nvdi search keyword log4j --limit 10
nvdi search keyword apache --min-score 7.0
```

### Monitor Products
```bash
nvdi monitor add nginx
nvdi monitor list-products
nvdi monitor watch nginx --interval 300
```

### Export Data
```bash
# Export to JSON
nvdi export cve CVE-2021-44228 --format json

# Export to CSV
nvdi export cve CVE-2021-44228 --format csv --output cve.csv

# Export specific fields only
nvdi export cve CVE-2021-44228 --fields "id,description,cvssv3" --format yaml

# Supported formats: json, csv, yaml, txt
```

### Database Management
```bash
# View database info
nvdi db info

# Clear all data
nvdi db clear
```

### Statistics
```bash
nvdi stats show
nvdi stats show --year 2023
```

## Configuration

Create a `.env` file:
```bash
NVD_API_KEY=your-api-key-here
```

Get your API key from: https://nvd.nist.gov/developers/request-an-api-key

## Available Fields

When using `--fields`, you can select from:
- `id`, `description`, `publishedDate`, `lastModifiedDate`
- `vulnStatus`, `sourceIdentifier`
- `cvssv3`, `cvssv2` (CVSS metrics)
- `references` (external links)
- `weaknesses` (CWE information)
- `configurations` (CPE data)
- `raw_data` (complete NVD response)

## Project Structure
```
nvdi/
├── nvdi_cli/           # Main package
│   ├── api/            # NVD API client
│   ├── commands/       # CLI commands
│   ├── db/             # SQLite database
│   ├── cache/          # Caching layer
│   ├── config/         # Configuration
│   └── utils/          # Utilities
├── .nvdi-data/         # Local database
├── .nvdi-cache/        # Cache directory
└── requirements.txt    # Dependencies
```

## Development

### Running Tests
```bash
./test.sh
```

This runs 39 comprehensive tests covering:
- CLI structure and commands
- Database operations (save, retrieve, search, reset)
- CVE retrieval (basic, full, field selection)
- Search functionality with CVSS filtering
- Export formats (JSON, CSV, YAML, TXT)
- Product monitoring
- Statistics generation

### Building Binary
```bash
./build.sh
```

Creates a standalone executable at `dist/nvdi` (~40-50MB) that includes:
- Python 3.x runtime
- All dependencies
- Rich terminal UI assets

The binary can be distributed without requiring users to install Python or any dependencies.

## License

MIT License - see [LICENSE](LICENSE)
