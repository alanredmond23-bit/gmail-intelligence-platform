# Secrets Management Setup

This project integrates with your OneDrive secrets and local development credentials.

## Available Secrets Locations

### OneDrive Secrets (Production/Shared)
```
~/Library/CloudStorage/OneDrive-Personal/SECRETS/
├── .wolf-secrets.env          # Master secrets
└── SECRETS_INVENTORY.csv      # Secrets catalog
```

### Local Secrets (Development)
```
~/.gmail-intelligence/
├── credentials.json           # Gmail OAuth2 credentials
├── token.json                 # Gmail API token (auto-generated)
└── config.yaml                # Application configuration
```

## Setup Instructions

### 1. Development Credentials (Local)

Store locally for development:

```bash
# Create local secrets directory
mkdir -p ~/.gmail-intelligence

# Copy Gmail credentials (you'll set this up via OAuth2 flow)
# See getting-started.md for OAuth2 setup
```

### 2. Automated Setup

The project can automatically load secrets from your OneDrive:

```python
# In src/gmail_intelligence/utils/config.py
from pathlib import Path

SECRETS_LOCATION = Path("~/Library/CloudStorage/OneDrive-Personal/SECRETS/").expanduser()
LOCAL_SECRETS = Path("~/.gmail-intelligence/").expanduser()

def load_secrets() -> dict:
    """Load secrets from OneDrive + local overrides."""
    secrets = {}

    # Load from OneDrive master secrets if available
    master_env = SECRETS_LOCATION / ".wolf-secrets.env"
    if master_env.exists():
        from dotenv import dotenv_values
        secrets.update(dotenv_values(master_env))

    # Override with local development credentials
    local_env = LOCAL_SECRETS / ".env"
    if local_env.exists():
        from dotenv import dotenv_values
        secrets.update(dotenv_values(local_env))

    return secrets
```

### 3. Environment Variables

**For Development**:
```bash
# ~/.gmail-intelligence/.env
GMAIL_CREDENTIALS_FILE=~/.gmail-intelligence/credentials.json
OPENAI_API_KEY=your-key-here
GMAIL_API_SCOPES=https://www.googleapis.com/auth/gmail.readonly
```

**From OneDrive** (automatically loaded):
- Master secrets in `.wolf-secrets.env`
- API keys, tokens, credentials

## Security Best Practices

### ✅ DO
- Store credentials in OneDrive (encrypted, synced, secure)
- Use `.gitignore` to exclude local secrets from git
- Use environment variables for all sensitive data
- Rotate credentials regularly
- Use app-specific passwords for Gmail

### ❌ DON'T
- Commit `.env` files to git
- Hardcode credentials in Python code
- Share credentials via email/chat
- Use personal passwords in code
- Store credentials in unencrypted text files

## Using Secrets in Code

### Example: Loading Gmail Credentials

```python
import os
from pathlib import Path
from gmail_intelligence.utils.config import load_secrets

# Load all secrets
secrets = load_secrets()

# Get specific secret
gmail_api_key = secrets.get("GMAIL_API_KEY")
openai_key = secrets.get("OPENAI_API_KEY")

# Or from environment
import os
gmail_credentials = os.getenv("GMAIL_CREDENTIALS_FILE")
```

### Example: Gmail OAuth2

```python
from gmail_intelligence.core.gmail_api import GmailAPIClient
from gmail_intelligence.utils.config import load_secrets

secrets = load_secrets()

client = GmailAPIClient(
    credentials_path=secrets["GMAIL_CREDENTIALS_FILE"],
    token_path=secrets.get("GMAIL_TOKEN_FILE", "~/.gmail-intelligence/token.json")
)

# First time: will open browser for OAuth2 consent
# Subsequent times: will use cached token
client.authenticate()
```

## Syncing Across Fleet

Since you have 3 machines (WORKHORSE, ADMIN, QUICKS):

### OneDrive Sync
```bash
# All machines automatically sync secrets from OneDrive
# Credentials stored at:
~/Library/CloudStorage/OneDrive-Personal/SECRETS/
```

### Fleet Deployment
```bash
# Deploy to all machines
fleet-deploy-all

# Or specific machine
deploy-supabase-mount WORKHORSE
```

## GitHub Secrets (CI/CD)

For GitHub Actions workflows, set these secrets:

```
Settings > Secrets & Variables > Actions > New repository secret
```

**Required Secrets**:
- `PYPI_API_TOKEN` - PyPI publishing
- `GITHUB_TOKEN` - (auto-provided)

**Optional Secrets**:
- `OPENAI_API_KEY` - For tests with real API
- `GMAIL_TEST_ACCOUNT` - Test account email
- `GMAIL_TEST_PASSWORD` - Test account app password

## Troubleshooting

### Secrets Not Loading
```bash
# Check OneDrive mount
ls ~/Library/CloudStorage/OneDrive-Personal/SECRETS/

# Check local secrets
ls ~/.gmail-intelligence/

# Debug in Python
from gmail_intelligence.utils.config import load_secrets
secrets = load_secrets()
print(secrets.keys())
```

### OAuth2 Token Expired
```bash
# Remove cached token to force re-authentication
rm ~/.gmail-intelligence/token.json

# Re-run setup
gmail-intelligence setup
```

### Permission Denied
```bash
# Fix OneDrive secrets permissions
chmod 600 ~/Library/CloudStorage/OneDrive-Personal/SECRETS/.wolf-secrets.env

# Fix local secrets
chmod 700 ~/.gmail-intelligence/
chmod 600 ~/.gmail-intelligence/.env
```

## Related Documentation

- [Getting Started](docs/getting-started.md) - OAuth2 setup
- [Deployment](docs/deployment.md) - Production secrets
- [DEVELOPERS.md](DEVELOPERS.md) - Security guidelines

---

**Last Updated**: 2026-02-07
**Status**: Ready for secrets integration
