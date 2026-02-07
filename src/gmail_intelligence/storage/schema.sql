-- Gmail Intelligence Platform - Supabase PostgreSQL Schema
-- Run these migrations in Supabase dashboard > SQL Editor

-- Create emails table
CREATE TABLE IF NOT EXISTS emails (
    id BIGSERIAL PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    gmail_id TEXT,
    from_address TEXT NOT NULL,
    to_addresses TEXT,
    cc_addresses TEXT,
    bcc_addresses TEXT,
    subject TEXT,
    body TEXT,
    html_body TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    thread_id TEXT,
    labels TEXT,  -- JSON array of labels
    sentiment VARCHAR(20),
    sentiment_confidence NUMERIC(3,2),
    is_privileged BOOLEAN DEFAULT false,
    privilege_confidence NUMERIC(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create attachments table
CREATE TABLE IF NOT EXISTS attachments (
    id BIGSERIAL PRIMARY KEY,
    email_id BIGINT NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    mime_type TEXT,
    size_bytes BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create entities table (NER - Named Entity Recognition)
CREATE TABLE IF NOT EXISTS entities (
    id BIGSERIAL PRIMARY KEY,
    email_id BIGINT NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,  -- PERSON, ORGANIZATION, LOCATION, etc
    entity_value TEXT NOT NULL,
    confidence NUMERIC(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create search_history table
CREATE TABLE IF NOT EXISTS search_history (
    id BIGSERIAL PRIMARY KEY,
    purpose TEXT NOT NULL,
    query TEXT,
    results_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_emails_from ON emails(from_address);
CREATE INDEX IF NOT EXISTS idx_emails_subject ON emails(subject);
CREATE INDEX IF NOT EXISTS idx_emails_timestamp ON emails(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_emails_sentiment ON emails(sentiment);
CREATE INDEX IF NOT EXISTS idx_emails_privileged ON emails(is_privileged);
CREATE INDEX IF NOT EXISTS idx_attachments_email ON attachments(email_id);
CREATE INDEX IF NOT EXISTS idx_entities_email ON entities(email_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_emails_body_fts ON emails USING GIN(to_tsvector('english', body));
CREATE INDEX IF NOT EXISTS idx_emails_subject_fts ON emails USING GIN(to_tsvector('english', subject));

-- Create RPC function for full-text search
CREATE OR REPLACE FUNCTION search_emails(
    query TEXT,
    max_results INT DEFAULT 50
)
RETURNS TABLE (
    id BIGINT,
    message_id TEXT,
    from_address TEXT,
    subject TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    sentiment VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.message_id,
        e.from_address,
        e.subject,
        e.timestamp,
        e.sentiment
    FROM emails e
    WHERE
        to_tsvector('english', e.body) @@ plainto_tsquery('english', query)
        OR to_tsvector('english', e.subject) @@ plainto_tsquery('english', query)
    ORDER BY ts_rank(to_tsvector('english', e.body || ' ' || COALESCE(e.subject, '')), plainto_tsquery('english', query)) DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at
CREATE TRIGGER update_emails_updated_at
    BEFORE UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Enable Row Level Security (RLS) for multi-tenancy
-- ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- Optional: Create policies for authenticated users
-- CREATE POLICY "Users can only access their own emails" ON emails
--     FOR ALL USING (auth.uid() = user_id);
