#!/usr/bin/env python3
"""Update results.json timestamp to current UTC time (ISO 8601 format)."""
import json
from datetime import datetime, timezone

path = 'data/results.json'
ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
with open(path, 'r+') as f:
    d = json.load(f)
    d['generated_at'] = ts
    f.seek(0)
    json.dump(d, f, indent=2)
    f.truncate()
print(f'Updated results.json timestamp to {ts}')
