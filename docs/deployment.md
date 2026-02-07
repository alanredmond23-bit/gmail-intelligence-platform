# Deployment Guide

## Prerequisites

- Python 3.10+
- Gmail API credentials (OAuth2 JSON file)
- Optional: Docker for containerized deployment

## Local Deployment

### 1. Install

```bash
git clone https://github.com/alanredmond/gmail-intelligence-platform.git
cd gmail-intelligence-platform
pip install -e .
```

### 2. Configure

```bash
# Set up credentials
cp config.example.yaml ~/.gmail-intelligence/config.yaml
# Edit config with your settings
```

### 3. Initialize Database

```bash
gmail-intelligence init-db
```

### 4. Run

```bash
gmail-intelligence search --purpose "Your search goal"
```

## Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["gmail-intelligence"]
```

Build and run:
```bash
docker build -t gmail-intelligence .
docker run -v ~/.gmail-intelligence:/root/.gmail-intelligence gmail-intelligence
```

## Production Considerations

- Use environment variables for sensitive credentials
- Set up automated backups of SQLite database
- Configure log rotation
- Enable error monitoring (Sentry, etc.)
- Use process supervisor (systemd, supervisor) for daemon mode

## Troubleshooting

### Authentication Errors
- Ensure Gmail account has API access enabled
- Check credentials file path and permissions
- Verify OAuth2 scopes are sufficient

### Performance
- Increase batch size in config for faster processing
- Use database indexes (already created)
- Consider using SSD for database location

### Memory Usage
- Monitor with `--progress` flag
- Adjust batch_size if memory spikes
- Consider running overnight for large extractions
