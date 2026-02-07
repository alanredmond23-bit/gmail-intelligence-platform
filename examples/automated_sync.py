"""Automated sync example."""

from gmail_intelligence.sync.scheduler import TaskScheduler
from gmail_intelligence.sync.incremental import IncrementalSync

# Create scheduler
scheduler = TaskScheduler()
sync = IncrementalSync()

# Schedule incremental sync every 30 minutes
scheduler.schedule_task(sync.sync_new_messages, interval_minutes=30)

print("Sync scheduled - running in background")
