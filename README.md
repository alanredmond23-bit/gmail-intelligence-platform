# Gmail Intelligence Platform

A unified, intelligent email extraction, organization, and analysis platform for desktop.

## Vision

Extract emails with purpose. Instead of keyword searches, describe **why** you're extracting emails—their context, intended outcomes, and desired organization. The platform intelligently finds, analyzes, and organizes them for your workflow.

## Key Features

- **Purpose-Driven Extraction** – Enter your search context and goals, not just keywords
- **Deep Semantic Search** – Fuzzy matching, semantic understanding, not just exact keywords
- **Flexible Output Options** – Export to folders, files, indexes, or structured databases
- **Gmail Integration** – Auto-organize with smart labels and folder creation
- **AI-Powered Analysis** – Sentiment analysis, entity extraction, privilege detection
- **Automated Sync** – Real-time incremental updates with History API
- **Error Recovery** – Self-healing mechanisms for robust operation
- **Regex & Advanced Filters** – Date ranges, senders, labels, and complex queries

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/alanredmond/gmail-intelligence-platform.git
cd gmail-intelligence-platform

# Install dependencies
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Set up Gmail OAuth2 credentials
gmail-intelligence setup

# Extract emails with a purpose
gmail-intelligence search \
  --purpose "Find all bankruptcy-related legal correspondence" \
  --output-format structured
```

## Architecture

The platform is organized into modular components:

- **core/** – IMAP and Gmail API clients, email parsing
- **search/** – Query building, semantic search, filtering
- **analysis/** – AI analysis (sentiment, entities, privilege detection)
- **storage/** – Database, file organization, full-text indexing
- **sync/** – Incremental sync, scheduled tasks, error recovery
- **gui/** – (Phase 2) Desktop application interface

## Roadmap

### Phase 1: Core CLI (Current)
- IMAP extraction engine
- Gmail API integration
- Basic search and filtering
- Local storage and indexing

### Phase 2: Desktop GUI
- PyQt6-based graphical interface
- Real-time preview and analysis
- Advanced visualization

### Phase 3: Advanced Features
- Multi-provider support (Outlook, Exchange)
- DAG workflow automation
- Sentiment analysis and classification
- Comprehensive test suite

## Development

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
# Generate API reference
python -m sphinx docs/
```

## Configuration

Configuration is stored in `data/config.yaml`:

```yaml
gmail:
  credentials_file: ~/.gmail/credentials.json
  tokens_file: ~/.gmail/token.json

storage:
  database: data/emails.db
  backup_dir: data/backups/

search:
  semantic_engine: openai
  batch_size: 50
```

## License

MIT License – see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

**Status**: 🔨 Under Active Development

For the full roadmap and architecture details, see [docs/](docs/).
