#!/usr/bin/env python3
import os
import subprocess
import json
from datetime import datetime, timedelta, timezone

VAULT_ADDR = os.environ.get('VAULT_ADDR')
VAULT_TOKEN = os.environ.get('VAULT_TOKEN')
VAULT_NAMESPACE = os.environ.get('VAULT_NAMESPACE', 'admin')

if not VAULT_ADDR or not VAULT_TOKEN:
    raise SystemExit("Please set VAULT_ADDR and VAULT_TOKEN environment variables.")

# Use a timezone-aware current UTC time
end_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

# Compute the start date 12 months ago
year = end_date.year
month = end_date.month
for _ in range(12):
    month -= 1
    if month == 0:
        month = 12
        year -= 1
start_date = datetime(year, month, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

last_auth = {}  # dictionary: client_id -> datetime of last auth
current = start_date

for i in range(12):
    month_start = current
    # Calculate next_month_start
    next_month_year = month_start.year
    next_month_month = month_start.month + 1
    if next_month_month == 13:
        next_month_month = 1
        next_month_year += 1
    next_month_start = datetime(next_month_year, next_month_month, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

    month_end = next_month_start - timedelta(seconds=1)

    start_str = month_start.isoformat().replace("+00:00", "Z")
    end_str = month_end.isoformat().replace("+00:00", "Z")

    print(f"Processing window: {start_str} to {end_str}", flush=True)

    url = f"{VAULT_ADDR}/v1/sys/internal/counters/activity/export?start_time={start_str}&end_time={end_str}&format=json"
    headers = ["X-Vault-Token: " + VAULT_TOKEN]
    if VAULT_NAMESPACE:
        headers.append("X-Vault-Namespace: " + VAULT_NAMESPACE)

    cmd = ["curl", "-sS"]
    for h in headers:
        cmd += ["--header", h]
    cmd += ["--request", "GET", url]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running curl: {result.stderr}", flush=True)
    else:
        # Print the raw output to see what's returned
        print("Raw API Response:")
        print(result.stdout)

        # Parse the response line-by-line, as the API returns NDJSON (one JSON object per line).
        lines = result.stdout.strip().split("\n")
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON line: {e}")
                print(f"Offending line: {line}")
                continue

            # Extract client_id and timestamp
            client_id = record.get("client_id")
            timestamp = record.get("timestamp")
            if client_id and timestamp:
                record_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if client_id not in last_auth or record_time > last_auth[client_id]:
                    last_auth[client_id] = record_time

    current = next_month_start

# Now we have last_auth with each client's last_auth_datetime.
# We need to produce a CSV with client_id, last_auth_timestamp, and roll_off_month.
# roll_off_month = same month as last_auth_timestamp but next year.
#
# For example, if last_auth_timestamp is 2024-07-03T15:48:13Z,
# roll_off_month should be 2025-07. We'll format roll_off_month as YYYY-MM.

output_file = "clients_last_auth.csv"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("client_id,last_auth_timestamp,roll_off_month\n")
    for cid, dt in last_auth.items():
        last_auth_str = dt.isoformat().replace("+00:00", "Z")
        roll_off_month = f"{dt.year + 1}-{dt.month:02d}"  # YYYY-MM format
        f.write(f"{cid},{last_auth_str},{roll_off_month}\n")

print(f"CSV output written to {output_file}")
