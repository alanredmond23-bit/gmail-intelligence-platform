"""Basic email extraction example."""

from gmail_intelligence.core.gmail_api import GmailAPIClient
from gmail_intelligence.storage.database import DatabaseManager
from gmail_intelligence.search.query_builder import QueryBuilder
from pathlib import Path

# Initialize client
gmail = GmailAPIClient(credentials_path="~/.gmail-intelligence/credentials.json")
gmail.authenticate()

# Build query
query = QueryBuilder().with_from("boss@example.com").with_subject("urgent").build()

# Get emails
messages = gmail.get_messages(query, max_results=50)

# Store in database
db = DatabaseManager(Path("~/.gmail-intelligence/emails.db"))
for msg in messages:
    db.insert_email(msg)

print(f"Extracted {len(messages)} emails")
