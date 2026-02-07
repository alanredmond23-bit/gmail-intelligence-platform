# Getting Started

## Installation

### Prerequisites
- Python 3.10 or later
- pip or conda
- Gmail account with API access enabled

### Setup

1. Clone the repository:
```bash
git clone https://github.com/alanredmond/gmail-intelligence-platform.git
cd gmail-intelligence-platform
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Initialize Gmail credentials:
```bash
gmail-intelligence setup
```

This will guide you through the OAuth2 flow to authenticate with Gmail.

## Basic Usage

### Search for Emails

```bash
gmail-intelligence search \
  --purpose "Find all legal correspondence from January 2025" \
  --output-format structured
```

### Output Options

- `json` - JSON format for programmatic access
- `csv` - CSV spreadsheet format
- `folder` - Organized into local folders
- `gmail` - Applied as labels in Gmail
- `structured` - Database format with full analysis

## Configuration

Configuration is stored in `~/.gmail-intelligence/config.yaml`:

```yaml
gmail:
  credentials_file: ~/.gmail-intelligence/credentials.json
  tokens_file: ~/.gmail-intelligence/token.json

storage:
  database: ~/.gmail-intelligence/emails.db
  backup_dir: ~/.gmail-intelligence/backups/

search:
  semantic_engine: openai
  batch_size: 50
  timeout_seconds: 300
```

## Next Steps

- Read [Architecture](architecture.md) for system design
- Check out [examples/](../examples/) for usage patterns
- Run tests with `pytest`
