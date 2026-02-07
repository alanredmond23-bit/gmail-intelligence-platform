# Database Architecture: Supabase PostgreSQL

## Overview

Gmail Intelligence Platform uses **Supabase PostgreSQL** for scalable, production-ready data storage with real-time capabilities.

**Your Project**: `fifybuzwfaegloijrmqb` (https://app.supabase.com)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Gmail Intelligence                       │
│                      Application                             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
    ┌────▼──────┐           ┌──────▼───────┐
    │ supabase_ │           │  database.py │
    │ client.py │◄──────────┤   (Interface)│
    └────┬──────┘           └──────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │  Supabase Client (REST API)                    │
    │  https://api.supabase.com/                     │
    └────┬──────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │  PostgreSQL 14+ Database                       │
    │  (fifybuzwfaegloijrmqb.supabase.co)           │
    │                                                │
    │  ├─ emails (email records)                     │
    │  ├─ attachments (file metadata)                │
    │  ├─ entities (NER results)                     │
    │  ├─ search_history (tracking)                  │
    │  ├─ Full-Text Search Indexes (GIN)             │
    │  ├─ PostgreSQL Functions (FTS)                 │
    │  └─ Triggers (auto timestamps)                 │
    └────┬──────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │  S3 Storage (Attachments)                      │
    │  ~/Supabase-S3/                                │
    │  (19 MB/s write, 3ms directory listing)        │
    └──────────────────────────────────────────────┘
```

---

## Data Model

### Emails Table
```
emails
├── id (BIGSERIAL PRIMARY KEY)
├── message_id (TEXT UNIQUE) ............ Gmail message ID
├── gmail_id (TEXT) ..................... Gmail thread ID
├── from_address (TEXT) ................. Sender email
├── to_addresses (TEXT) ................. Recipient list (JSON)
├── subject (TEXT) ...................... Email subject
├── body (TEXT) ......................... Email body (full text)
├── html_body (TEXT) .................... HTML version
├── timestamp (TIMESTAMP TZ) ............ Sent date
├── thread_id (TEXT) .................... Gmail thread ID
├── labels (TEXT) ....................... Gmail labels (JSON)
├── sentiment (VARCHAR) ................. Analysis result
├── sentiment_confidence (NUMERIC) ...... Confidence 0-1
├── is_privileged (BOOLEAN) ............. Privilege flag
├── privilege_confidence (NUMERIC) ...... Confidence 0-1
├── created_at (TIMESTAMP TZ) ........... Stored timestamp
└── updated_at (TIMESTAMP TZ) ........... Last modified

Indexes:
├── PRIMARY KEY (id)
├── UNIQUE (message_id)
├── INDEX (from_address)
├── INDEX (timestamp DESC)
├── INDEX (sentiment)
├── INDEX (is_privileged)
├── FTS INDEX (body) .................... Full-text search
└── FTS INDEX (subject)
```

### Attachments Table
```
attachments
├── id (BIGSERIAL PRIMARY KEY)
├── email_id (BIGINT FK) ................ Reference to emails
├── filename (TEXT) ..................... Original filename
├── file_path (TEXT) .................... S3 path
├── mime_type (TEXT) .................... Content type
├── size_bytes (BIGINT) ................. File size
└── created_at (TIMESTAMP TZ) ........... Created timestamp

Indexes:
├── PRIMARY KEY (id)
└── INDEX (email_id)
```

### Entities Table
```
entities
├── id (BIGSERIAL PRIMARY KEY)
├── email_id (BIGINT FK) ................ Reference to emails
├── entity_type (TEXT) .................. PERSON, ORG, LOCATION
├── entity_value (TEXT) ................. Extracted text
├── confidence (NUMERIC) ................ 0-1 confidence
└── created_at (TIMESTAMP TZ) ........... Created timestamp

Indexes:
├── PRIMARY KEY (id)
├── INDEX (email_id)
└── INDEX (entity_type)
```

### Search History Table
```
search_history
├── id (BIGSERIAL PRIMARY KEY)
├── purpose (TEXT) ...................... Why search was done
├── query (TEXT) ........................ Query executed
├── results_count (INTEGER) ............. Results found
└── created_at (TIMESTAMP TZ) ........... Timestamp

Use Case: Track searches for analytics
```

---

## Relationships

```
emails (1) ──────────────────────── (M) attachments
  │
  └──────────────────────────────── (M) entities
```

- **emails.id** ← attachments.email_id
- **emails.id** ← entities.email_id
- Cascade delete: Removing email removes related attachments and entities

---

## Key Features

### 1. Full-Text Search
```sql
-- PostgreSQL FTS on body and subject
search_emails(query TEXT, max_results INT)
```

**Usage**:
```python
results = db.search_emails("bankruptcy lawsuit", limit=20)
```

### 2. Indexes for Performance

| Index | Purpose | Query Type |
|-------|---------|-----------|
| from_address | Filter by sender | WHERE from_address = '...' |
| timestamp DESC | Date range queries | WHERE timestamp > ... |
| sentiment | Sentiment filtering | WHERE sentiment = 'positive' |
| is_privileged | Privilege detection | WHERE is_privileged = true |
| FTS (body, subject) | Full-text search | to_tsvector() @@ plainto_tsquery() |

### 3. Automatic Timestamps
- `created_at`: Set on insert (CURRENT_TIMESTAMP)
- `updated_at`: Auto-updated on any modification (TRIGGER)

### 4. Data Integrity
- Primary keys on all tables
- Foreign key constraints (attachments, entities)
- Unique constraint on message_id (prevents duplicates)

---

## Performance Characteristics

### Inserts
```python
# Single insert: ~50ms
db.insert_email(email_dict)

# Batch insert: ~2-5ms per email
db.batch_insert_emails(1000_emails)  # ~2-5 seconds total
```

### Queries
```python
# Filter by indexed column: ~10-50ms
db.query_emails(where="from_address=eq.test@example.com", limit=100)

# Full-text search: ~50-200ms
db.search_emails("bankruptcy", limit=50)

# Pagination: Constant time regardless of offset
db.query_emails(limit=10, offset=1000)
```

### Concurrent Operations
- Supabase handles up to 100+ concurrent connections
- Connection pooling enabled by default
- Row-level locking for updates

---

## S3 Integration

Attachments stored on **Supabase S3** mount:

```
~/Supabase-S3/
├── attachments/
│   ├── email_123/
│   │   ├── document.pdf
│   │   ├── image.png
│   │   └── archive.zip
│   └── email_456/
│       └── contract.docx
└── backups/
    ├── 20260207.sql
    └── 20260206.sql
```

**Performance**: 19 MB/s write, 3ms directory listing

**Fleet Sync**: All machines (WORKHORSE, ADMIN, QUICKS) access same S3 mount

---

## Multi-Tenant Support

### Optional: Row-Level Security (RLS)

Enable per-user data isolation:

```sql
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_see_own_emails" ON emails
  FOR ALL USING (auth.uid()::text = user_id);
```

Currently disabled for single-user usage. Enable when needed.

---

## Real-Time Subscriptions

### Enable Real-Time Monitoring

```python
from supabase import create_client

client = create_client(supabase_url, supabase_key)

# Subscribe to email changes
channel = client.realtime.subscribe("emails")
channel.on("INSERT", lambda x: print(f"New email: {x['data']['message_id']}"))
channel.on("UPDATE", lambda x: print(f"Updated: {x['data']['id']}"))
channel.subscribe()
```

### Use Cases
- Live dashboard updates
- Incremental sync notifications
- Real-time privilege alerts
- Analysis completion notifications

---

## Backup & Recovery

### Automated Backups
- Supabase backs up daily
- Point-in-time recovery available
- Backup retention: 7 days (default)

### Manual Backup

```bash
# Backup to file
pg_dump --data-only $SUPABASE_URL -U postgres > backup.sql

# Backup to S3
pg_dump --data-only $SUPABASE_URL -U postgres | \
  gzip > ~/Supabase-S3/backups/$(date +%Y%m%d).sql.gz
```

---

## Security

### Network Security
- All connections HTTPS/TLS
- Supabase handles SSL termination
- No exposed database port

### Authentication
- **Anon Key**: Public API key, use for frontend
- **Service Key**: Private, for backend/admin operations
- Both keys in environment variables (not committed to git)

### Row-Level Security (RLS)
- Optional per-user data isolation
- Policies enforce access control at database level
- Automatically applied to all queries

### Rate Limiting
- Supabase enforces rate limits
- Implement backoff on rate limit errors
- See error_recovery.py for retry logic

---

## Monitoring & Debugging

### In Supabase Dashboard

1. **Database > Query Performance**
   - View slowest queries
   - Identify missing indexes

2. **Database > Connections**
   - Monitor active connections
   - Kill stuck queries

3. **Logs > Database**
   - View all database operations
   - Search for errors

### In Python

```python
# Check connection
from gmail_intelligence.storage.database import DatabaseManager

db = DatabaseManager()
stats = db.get_stats()
print(f"Connected: {stats['status']}")
print(f"Total emails: {stats['total_emails']}")
```

---

## Optimization Tips

### Query Optimization
1. **Use pagination** for large result sets
2. **Index on WHERE clauses** (already created)
3. **Limit projections** to needed columns
4. **Batch operations** for bulk work

### Application Optimization
1. **Connection pooling** (automatic)
2. **Cache frequently accessed data** (Redis - future)
3. **Async queries** for non-blocking operations
4. **Incremental sync** instead of full refresh

---

## Cost Considerations

### Supabase Pricing Tiers

**Free Tier**:
- 500 MB database
- 1 GB file storage
- 2-core CPU
- Good for development/testing

**Pro Tier** ($25/month):
- 8 GB database
- 100 GB file storage
- 2-core CPU (scalable)
- Suitable for production

**Enterprise**:
- Custom database size
- Custom file storage
- Dedicated resources
- SLA guarantees

### Optimization for Cost
- Use S3 for attachments (separate storage)
- Archive old emails to cold storage
- Implement data retention policies
- Monitor storage growth

---

## Migration Path

If switching from another database:

1. **Prepare schema** (done: schema.sql)
2. **Migrate data** with bulk insert
3. **Validate data** integrity
4. **Test queries** and performance
5. **Cut over** to new database

See migration examples in Phase 2 implementation.

---

## Next Steps

1. ✅ Get Supabase credentials
2. ✅ Run schema.sql in SQL Editor
3. ✅ Set SUPABASE_URL and SUPABASE_KEY
4. ✅ Test connection: `db.initialize()`
5. ✅ Begin Phase 2: IMAP & Gmail API implementation

---

**Database Architecture Complete! Ready for Phase 2.** 🚀
