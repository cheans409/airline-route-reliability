# U.S. Airline Route Reliability

**Which routes should an airline operations team prioritize for reliability improvements?**

An operations analytics project using official U.S. Bureau of Transportation Statistics (BTS) flight records to compare delays, cancellations, and diversions across routes, airlines, and seasons.

**Status: project setup and initial data acquisition. Analysis and dashboard are not yet complete.**

## Business objective

Identify routes where substantial flight volume coincides with persistent reliability problems. The intended output is a transparent shortlist for operational investigation, supported by an interactive dashboard and a short decision memo. Observed associations will not be presented as proof of causes or achievable savings.

## Dataset and scope

- **Source:** BTS, Reporting Carrier On-Time Performance (1987–present).
- **Official downloads:** [Monthly ZIP archives](https://www.transtats.bts.gov/PREZIP/).
- **Documentation:** [BTS on-time statistics](https://www.transtats.bts.gov/ot_delay/).
- **Planned analysis window:** January–December 2025, a complete calendar year.
- **Initial acquisition:** January 2025, with 539,747 records covering January 1–31; the downloaded file and checksum are recorded in [the source manifest](data/source_manifest.json).
- **Grain:** one reported flight record. Routes are directional: origin → destination.
- **Coverage:** reporting carriers' domestic operations, not every flight worldwide or every U.S. operator.

The first phase measures **flights**, not passengers. Passenger traffic from BTS T-100 may be added later after verifying carrier, geography, and period compatibility. On-time records do not directly establish passenger counts or route profitability.

## Questions

1. Which sufficiently busy routes have the highest cancellation and late-arrival rates?
2. Are poor results persistent across months or concentrated in particular seasons?
3. How do carriers compare on shared routes, accounting for schedule and route mix?
4. Which routes merit investigation based on both disruption frequency and affected flight volume?

## Planned stack

Python for acquisition and validation; PostgreSQL for data modeling and analysis; Tableau for an operations dashboard. The initial downloader uses only Python's standard library.

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

## Repository structure

```text
 data/
   raw/                   # Downloaded official archives (ignored)
   processed/             # Cleaned outputs (ignored)
   source_manifest.json   # Source URLs and checksums
 docs/
   project_plan.md        # Milestones and acceptance criteria
   metrics.md             # Proposed denominators and comparison rules
 scripts/
   download_data.py       # Monthly acquisition and integrity checks
   inspect_data.py        # Schema, date coverage, and row-count checks
 sql/                     # Planned schema, QA, and analytical queries
 dashboards/              # Dashboard specification; workbook will follow
 reports/                 # Data inspection and eventual decision memo
```

## Milestones

- [x] Select an official dataset and define the business question.
- [x] Build acquisition tooling and document the source.
- [x] Inspect January: required columns present and dates within the expected month.
- [ ] Acquire and validate all 12 months.
- [ ] Build PostgreSQL staging and analytical tables.
- [ ] Validate metric denominators and duplicate handling.
- [ ] Analyze routes, carriers, and seasonality.
- [ ] Publish a Tableau dashboard and evidence-backed recommendations.

See [the project plan](docs/project_plan.md) and [metric definitions](docs/metrics.md). No analytical findings are claimed at this stage.
