# Reproducing the analysis

Technical instructions for the [airline reliability report](../README.md). Run all commands from the repository root.

## Quick start

Requires Python 3.9+ and internet access. Run from the repository root:

```bash
python3 scripts/download_data.py --year 2025 --month 1
python3 scripts/inspect_data.py --year 2025 --month 1
```

The download script validates the ZIP and records its URL, size, SHA-256 checksum, and first-recorded timestamp. Existing local archives are reused and validated. Large source files stay outside Git; the small manifest and inspection report are versioned.

To acquire the planned full year when ready:

```bash
for month in 1 2 3 4 5 6 7 8 9 10 11 12; do
  python3 scripts/download_data.py --year 2025 --month "$month"
done
```

Allow several hundred MB for compressed annual data and more space for extraction. If Python reports a certificate error, configure your machine's trusted CA certificates; do not disable TLS verification.

## PostgreSQL pipeline

Requires a running PostgreSQL server (validated on PostgreSQL 18.6), `createdb`, and Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
createdb airline_reliability  # Once, if the database does not already exist
python3 scripts/load_postgres.py --year 2025 --month 1
python3 -m unittest discover -s tests -v
python3 scripts/export_results.py
```

The default connection uses local PostgreSQL and `dbname=airline_reliability`. Set `DATABASE_URL` for another connection; never commit credentials. Tables live in the dedicated `airline` schema. The database user needs schema/table creation privileges.

Each load verifies the manifest checksum and source fields, then atomically replaces only its selected month. Duplicate flight keys, invalid values, and mismatched totals abort the transaction, preserving the prior successful load. Raw analytical fields remain text in staging; the complete source records remain in the original ZIP, identified by checksum and CSV data-row number (starting at 1, excluding the header). No rows are silently discarded. Airport and carrier mappings are month-specific views rather than permanent code-to-ID assumptions.

Exports include [monthly totals](../reports/monthly_summary.csv), [quality checks](../reports/load_quality.csv), [a preliminary route shortlist](../reports/priority_routes.csv), and [volume-threshold sensitivity](../reports/threshold_sensitivity.csv). The shortlist ranks **observed disrupted flight counts** among carrier-routes with at least 100 monthly flights; it does not estimate avoidable disruptions or passenger impacts.

