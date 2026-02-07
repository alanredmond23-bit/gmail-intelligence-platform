# Supabase PostgreSQL Setup Guide

Gmail Intelligence Platform uses **Supabase** for scalable PostgreSQL database with real-time capabilities.

## Your Supabase Project

**Project ID**: `fifybuzwfaegloijrmqb`
**Dashboard**: https://app.supabase.com/

---

## Setup Steps

### 1. Get Your Credentials

In Supabase Dashboard:

1. Go to **Settings > API**
2. Copy these values:
   - **Project URL**: `https://fifybuzwfaegloijrmqb.supabase.co` (or your custom domain)
   - **Anon Key**: Your public API key
   - **Service Key**: Your secret key (keep private!)

### 2. Set Environment Variables

Create `~/.gmail-intelligence/.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://fifybuzwfaegloijrmqb.supabase.co
SUPABASE_KEY=your-anon-key-here

# Optional: Service key for admin operations
SUPABASE_SERVICE_KEY=your-service-key-here
```

Or set as environment variables:

```bash
export SUPABASE_URL="https://fifybuzwfaegloijrmqb.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### 3. Initialize Database Schema

In Supabase Dashboard:

1. Go to **SQL Editor**
2. Create a new query
3. Copy-paste the entire contents of `src/gmail_intelligence/storage/schema.sql`
4. Click **Run**

This creates:
- ✅ `emails` table (main storage)
- ✅ `attachments` table (for files)
- ✅ `entities` table (for NER)
- ✅ `search_history` table (for tracking)
- ✅ Indexes for performance
- ✅ Full-text search function
- ✅ Update triggers

---

## Database Schema Overview

### emails table
```sql
emails (
  id BIGSERIAL PRIMARY KEY,
  message_id TEXT UNIQUE,      -- Gmail message ID
  from_address TEXT,           -- Sender email
  subject TEXT,                -- Email subject
  body TEXT,                   -- Email body
  timestamp TIMESTAMP,         -- Sent date
  sentiment VARCHAR,           -- Sentiment analysis result
  is_privileged BOOLEAN,       -- Attorney-client privilege flag
  created_at TIMESTAMP,        -- When stored
  updated_at TIMESTAMP         -- Last modified
)
```

### attachments table
```sql
attachments (
  id BIGSERIAL PRIMARY KEY,
  email_id BIGINT REFERENCES emails,
  filename TEXT,               -- Original filename
  file_path TEXT,              -- Local storage path
  mime_type TEXT,              -- Content type
  size_bytes BIGINT            -- File size
)
```

### entities table
```sql
entities (
  id BIGSERIAL PRIMARY KEY,
  email_id BIGINT REFERENCES emails,
  entity_type TEXT,            -- PERSON, ORGANIZATION, LOCATION
  entity_value TEXT,           -- Entity text (e.g., "John Smith")
  confidence NUMERIC           -- Extraction confidence (0-1)
)
```

---

## Usage in Code

### Basic Usage

```python
from gmail_intelligence.storage.database import DatabaseManager

# Initialize (credentials from env)
db = DatabaseManager()
db.initialize()

# Insert email
email_id = db.insert_email({
    "message_id": "abc123def456",
    "from_address": "sender@example.com",
    "subject": "Contract Review",
    "body": "Please review the attached contract...",
    "timestamp": "2026-02-07T10:30:00Z"
})

# Query emails
emails = db.query_emails(limit=10)

# Search emails
results = db.search_emails("bankruptcy", limit=20)

# Update email with analysis
db.update_email(email_id, {
    "sentiment": "formal",
    "sentiment_confidence": 0.92,
    "is_privileged": True
})

# Insert extracted entities
db.insert_entities(email_id, [
    {"type": "PERSON", "value": "John Smith", "confidence": 0.95},
    {"type": "ORGANIZATION", "value": "Acme Corp", "confidence": 0.88}
])
```

### Batch Operations

```python
# Batch insert for performance
emails = [
    {"message_id": "msg1", "from_address": "a@example.com", ...},
    {"message_id": "msg2", "from_address": "b@example.com", ...},
]
email_ids = db.batch_insert_emails(emails)
```

### Full-Text Search

```python
# Search using PostgreSQL full-text search
results = db.search_emails("bankruptcy lawsuit", limit=50)

# Get statistics
stats = db.get_stats()
print(f"Total emails: {stats['total_emails']}")
```

---

## Fleet Integration

Since you have Supabase mounted at `~/Supabase-S3`:

### S3 Storage for Attachments

```python
from pathlib import Path

# Supabase S3 mount available on all fleet machines
s3_path = Path("~/Supabase-S3").expanduser()

# Store attachments here
attachment_path = s3_path / "attachments" / "email_123" / "document.pdf"
```

### Fleet Synchronization

All machines (WORKHORSE, ADMIN, QUICKS) access the same Supabase database:

```bash
# Verify Supabase is mounted on all machines
fleet-status

# Deploy application to all machines
fleet-deploy-all

# Sync Supabase mount
supa-mount status
```

---

## Real-Time Features

### Enable Real-Time

In Supabase Dashboard:

1. **Database > Replication**
2. Check the tables you want to monitor:
   - ✅ emails
   - ✅ attachments
   - ✅ entities

3. Subscribe to real-time changes in code:

```python
from supabase import create_client

client = create_client(supabase_url, supabase_key)

# Listen for email insertions
channel = client.realtime.subscribe("emails")
channel.on("INSERT", callback=lambda x: print(f"New email: {x}"))
channel.subscribe()

# Run event loop
import asyncio
asyncio.run(asyncio.sleep(60))
```

---

## Row-Level Security (Optional)

For multi-tenant or per-user data isolation:

### Enable RLS

```sql
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see only their own emails" ON emails
  FOR SELECT USING (auth.uid()::text = user_id);
```

---

## Backups

Supabase automatically backs up daily. Access backups:

1. **Settings > Backups**
2. Download or restore point-in-time backups

### Custom Backup Script

```bash
#!/bin/bash
# Backup Supabase to local file
pg_dump --data-only $SUPABASE_URL -U postgres > emails_backup.sql

# Or backup to Supabase-S3
pg_dump --data-only $SUPABASE_URL -U postgres > ~/Supabase-S3/backups/$(date +%Y%m%d).sql
```

---

## Performance Optimization

### Query Optimization

1. **Pagination** for large result sets:
```python
# Get page 2, 10 items per page
emails = db.query_emails(limit=10, offset=10)
```

2. **Indexes** (already created):
   - from_address
   - timestamp
   - sentiment
   - is_privileged
   - Full-text search on body/subject

3. **Batch operations** for bulk inserts:
```python
# Much faster than individual inserts
db.batch_insert_emails(1000_emails)
```

---

## Troubleshooting

### Connection Issues

```python
from gmail_intelligence.storage.database import DatabaseManager

try:
    db = DatabaseManager()
    stats = db.get_stats()
    print(f"✅ Connected: {stats}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    # Check:
    # 1. SUPABASE_URL and SUPABASE_KEY set
    # 2. Project active on Supabase dashboard
    # 3. Network connectivity
```

### Schema Not Found

If `initialize()` fails:

1. Verify schema.sql was executed in Supabase dashboard
2. Check table exists:
   ```bash
   curl -X GET "https://fifybuzwfaegloijrmqb.supabase.co/rest/v1/emails" \
     -H "Authorization: Bearer YOUR_KEY"
   ```

3. Re-run schema.sql if needed

### Slow Queries

1. Add indexes (already done in schema.sql)
2. Use `LIMIT` and pagination
3. Avoid `SELECT *` - specify columns
4. Monitor query performance in Supabase dashboard > Database > Slowlog

---

## Useful Resources

- **Supabase Docs**: https://supabase.com/docs
- **PostgREST API**: https://postgrest.org/
- **Real-Time Guide**: https://supabase.com/docs/guides/realtime
- **RLS Guide**: https://supabase.com/docs/guides/auth/row-level-security

---

## Next Steps

1. ✅ Set up Supabase credentials
2. ✅ Run schema.sql in SQL Editor
3. ✅ Test connection with `db.initialize()`
4. ✅ Begin Phase 2 implementation

---

**Project Ready for Database Operations!** 🚀
