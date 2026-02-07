"""Legal workflow example - extract emails for legal discovery."""

from gmail_intelligence.core.gmail_api import GmailAPIClient
from gmail_intelligence.analysis.privilege_detector import PrivilegeDetector
from gmail_intelligence.search.query_builder import QueryBuilder
from gmail_intelligence.storage.database import DatabaseManager
from pathlib import Path

# Initialize
gmail = GmailAPIClient(credentials_path="~/.gmail-intelligence/credentials.json")
gmail.authenticate()
privilege_detector = PrivilegeDetector()
db = DatabaseManager(Path("~/.gmail-intelligence/emails.db"))

# Search for legal correspondence
query = QueryBuilder()\
    .with_from("lawyer@firm.com")\
    .with_subject("legal")\
    .build()

messages = gmail.get_messages(query)

# Analyze for privilege
for msg in messages:
    privilege_info = privilege_detector.detect_privilege(msg)
    msg["is_privileged"] = privilege_info.get("privileged", False)
    msg["privilege_confidence"] = privilege_info.get("confidence", 0.0)

    # Store with privilege metadata
    db.insert_email(msg)

# Create label for privileged emails
gmail.create_label("PRIVILEGED - DO NOT PRODUCE")

print(f"Processed {len(messages)} legal emails")
print("Privileged emails flagged for review")
