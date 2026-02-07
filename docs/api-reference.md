# API Reference

## Core Module

### IMAPClient
```python
class IMAPClient:
    def connect(email: str, password: str) -> bool
    def search(query: str) -> list[str]
    def fetch_email(uid: str) -> dict
```

### GmailAPIClient
```python
class GmailAPIClient:
    def authenticate() -> bool
    def get_messages(query: str, max_results: int = 100) -> list[dict]
    def create_label(label_name: str) -> str
    def apply_label(message_id: str, label_id: str) -> bool
```

## Search Module

### QueryBuilder
```python
class QueryBuilder:
    def with_from(email: str) -> QueryBuilder
    def with_to(email: str) -> QueryBuilder
    def with_subject(subject: str) -> QueryBuilder
    def build() -> str
```

### SemanticSearch
```python
class SemanticSearch:
    def search(purpose: str, emails: list[dict]) -> list[dict]
```

## Analysis Module

### SentimentAnalyzer
```python
class SentimentAnalyzer:
    def analyze(text: str) -> dict  # { sentiment: str, confidence: float }
```

### EntityExtractor
```python
class EntityExtractor:
    def extract_entities(text: str) -> dict  # { type: [values] }
```

### PrivilegeDetector
```python
class PrivilegeDetector:
    def detect_privilege(email: dict) -> dict  # { privileged: bool, confidence: float }
```

## Storage Module

### DatabaseManager
```python
class DatabaseManager:
    def initialize() -> bool
    def insert_email(email: dict) -> int
    def query_emails(query: str) -> list[dict]
```

### FileManager
```python
class FileManager:
    def save_email(email: dict, folder: str = "") -> Path
```

## Sync Module

### IncrementalSync
```python
class IncrementalSync:
    def sync_new_messages() -> dict  # { synced: int, errors: int }
```

### TaskScheduler
```python
class TaskScheduler:
    def schedule_task(task: Callable, interval_minutes: int) -> bool
```

---

For detailed examples and integration patterns, see [Getting Started](getting-started.md).
