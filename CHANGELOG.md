# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-07

### Added
- Initial project structure with modular architecture
- Complete directory organization: core, search, analysis, storage, sync, utils, gui
- Comprehensive pyproject.toml with all dependencies
- Database schema (SQLite) for emails, attachments, entities
- CLI framework with Typer
- Test suite with pytest fixtures
- CI/CD workflows (GitHub Actions)
- Documentation: Getting Started, Architecture, API Reference, Deployment
- Practical examples: basic extraction, automated sync, legal workflow
- MIT License

### Components
- **Core**: IMAP client, Gmail API client, email parser, attachment handler (stubs)
- **Search**: Query builder, semantic search, filtering (stubs)
- **Analysis**: Sentiment, entity extraction, classification, privilege detection (stubs)
- **Storage**: Database manager, file manager, full-text indexer (stubs)
- **Sync**: Incremental sync, task scheduler, error recovery (stubs)
- **Utils**: Config management, logging, progress tracking

### Status
🔨 Framework complete, implementation phase beginning

---

## [Unreleased]

### In Development
- Phase 2: Core implementation of IMAP and Gmail API
- Database CRUD operations
- Semantic search integration with OpenAI
- Full-text indexing
- Error recovery mechanisms
- Desktop GUI (PyQt6)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
