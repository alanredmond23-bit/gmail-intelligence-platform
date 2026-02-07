# Architecture

## System Design

The Gmail Intelligence Platform is built with a modular, layered architecture:

```
┌─────────────────────────────────────────┐
│           CLI / GUI Interface           │
├─────────────────────────────────────────┤
│        Search & Analysis Layer          │
│  (Query Builder, Semantic Search, ML)   │
├─────────────────────────────────────────┤
│    Core Extraction Layer                │
│  (IMAP, Gmail API, Email Parser)        │
├─────────────────────────────────────────┤
│    Storage & Sync Layer                 │
│  (Database, Files, Incremental Sync)    │
├─────────────────────────────────────────┤
│    External Services                    │
│  (Gmail API, OpenAI, Google Cloud)      │
└─────────────────────────────────────────┘
```

## Components

### Core (Extraction)
- **IMAP Client** - Direct IMAP connection to email servers
- **Gmail API Client** - OAuth2 authenticated Gmail access
- **Email Parser** - Parse RFC822 messages
- **Attachment Handler** - Extract and manage attachments

### Search
- **Query Builder** - Build Gmail search queries
- **Semantic Search** - AI-powered fuzzy matching
- **Filters** - Date, sender, label filtering

### Analysis
- **Sentiment Analyzer** - Emotional tone detection
- **Entity Extractor** - People, organizations, locations
- **Classifier** - Email categorization
- **Privilege Detector** - Attorney-client privilege flagging

### Storage
- **Database Manager** - SQLite email store
- **File Manager** - Local file organization
- **Indexer** - Full-text search indexes

### Sync
- **Incremental Sync** - Gmail History API integration
- **Task Scheduler** - Cron/timer-based tasks
- **Error Recovery** - Self-healing mechanisms

## Data Flow

```
User Purpose
    ↓
Query Builder → Semantic Search
    ↓
Gmail API / IMAP
    ↓
Email Parser → Attachment Handler
    ↓
Analysis Engine (Sentiment, Entities, Privilege)
    ↓
Storage (Database, Files, Index)
    ↓
Output (JSON, CSV, Gmail Labels, Folders)
```

## Design Patterns

- **Dependency Injection** - Easily swap implementations
- **Plugin Architecture** - Extensible analyzer components
- **Async/Await** - Non-blocking I/O operations
- **Event-Driven** - Pub/sub for sync and notifications

See [API Reference](api-reference.md) for detailed interface documentation.
