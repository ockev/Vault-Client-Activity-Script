# Vault Client Activity Script

A Python-based utility to query Vault's internal activity counters over the past 12 months, identify the latest authentication timestamp per client, and calculate a "roll off month" (one year after their last authentication) to forecast what a 12 month usage may look like. The script then exports the results to a CSV file.

## Overview

This script helps Vault administrators, Solutions Engineers, and DevOps teams understand when each Vault client last authenticated for estimations in 12 month billing cycles.  Understanding Vault client authentication patterns is crucial for capacity planning, budgeting, and license management.

### Key Features:

- Iterates through the last 12 months of authentication activity using the Vault `/v1/sys/internal/counters/activity/export` endpoint.
- Supports newline-delimited JSON (NDJSON) responses from Vault.
- Extracts `client_id` and their latest authentication timestamp.
- Calculates a "roll off month" for each client, one year after their last recorded authentication month.
- Outputs a CSV file (`clients_last_auth.csv`) with `client_id`, `last_auth_timestamp`, and `roll_off_month`.

## Prerequisites

- **Python 3.6+:**
  - The script uses Python 3 standard library modules (`datetime`, `subprocess`, `json`).
  - Ensure you have Python 3.6 or later installed.

- **Vault Environment Variables:**
  - Set the following environment variables:
    - `VAULT_ADDR`: The address of your Vault instance (e.g., `https://your-vault-url:8200`).
    - `VAULT_TOKEN`: A token with permissions to call `sys/internal/counters/activity/export`.
    - `VAULT_NAMESPACE` (optional if using Enterprise namespaces): The namespace to query.

- **curl:**
  - The script uses `curl` to query the Vault API. Ensure `curl` is installed and available on your PATH.

- **Network Access:**
  - The machine running the script must have connectivity to your Vault instance.

## Usage

### 1. Set Environment Variables:

```bash
export VAULT_ADDR="https://your-vault-url:8200"
export VAULT_TOKEN="s.your-vault-token"
export VAULT_NAMESPACE="admin"  # Omit if not using namespaces
```

### 2. Run the Script:
```bash
python3 track_vault_clients.py
```

- **As it runs, the script:**
  - Iterates month-by-month over the last 12 months.
  - Fetches activity records from Vault.
  - Prints raw responses for debugging.
  - Outputs a CSV file named clients_last_auth.csv.
 
### 3. Review the CSV Output:
- Once complete, open or review the CSV file:
```bash
cat clients_last_auth.csv
```
- Example Output:
```bash
client_id,last_auth_timestamp,roll_off_month
9da4533e-c136-ace3-bf23-a13503a71f34,2024-07-03T15:48:13Z,2025-07
e03019c9-191e-a057-2a03-9fa81acf529b,2024-07-03T19:11:04Z,2025-07
```

## Example Commands
- Basic Run:
```bash
VAULT_ADDR="https://vault.example.com" \
VAULT_TOKEN="s.abc123..." \
python3 track_vault_clients.py
```

- Review Logs
  - The script prints raw API responses for each month, which can help in troubleshooting.
 
## Troubleshooting

- **Empty or Invalid Responses:**
  - If the script reports JSON parsing errors, ensure you have the correct token permissions and a reachable Vault instance returning valid data.

- **Date/Time Issues:**
  - The script uses UTC-based calculations. Adjust if needed for your environment.

- **No Results:**
  - If `clients_last_auth.csv` is empty, verify that there were authenticated clients in the past 12 months, and confirm your environment variables and namespace settings.# Vault-Client-Activity-Script
