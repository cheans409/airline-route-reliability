"""Inspect a downloaded month without extracting or modifying the source CSV."""
import argparse
import csv
import io
import json
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'FlightDate', 'DOT_ID_Reporting_Airline', 'OriginAirportID',
            'DestAirportID', 'Cancelled', 'Diverted', 'ArrDel15', 'ArrDelayMinutes'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=2025)
    parser.add_argument('--month', type=int, choices=range(1, 13), default=1)
    args = parser.parse_args()
    archive_path = ROOT / 'data/raw' / f'On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{args.year}_{args.month}.zip'
    dates, missing = Counter(), Counter()
    count = 0
    with zipfile.ZipFile(archive_path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(members) != 1:
            raise ValueError('Expected exactly one source CSV')
        with archive.open(members[0]) as source:
            reader = csv.DictReader(io.TextIOWrapper(source, encoding='utf-8-sig'))
            fields = reader.fieldnames
            absent = REQUIRED - set(fields or [])
            if absent:
                raise ValueError(f'Missing required columns: {sorted(absent)}')
            for row in reader:
                observed = date.fromisoformat(row['FlightDate'])
                if (observed.year, observed.month) != (args.year, args.month):
                    raise ValueError(f'Unexpected flight date: {observed}')
                count += 1
                dates[str(observed)] += 1
                missing.update(k for k in REQUIRED if not row[k].strip())
    if not count:
        raise ValueError('Empty source CSV')
    report = {
        'source_archive': str(archive_path.relative_to(ROOT)),
        'rows': count, 'date_min': min(dates), 'date_max': max(dates),
        'distinct_dates': len(dates), 'columns': [f for f in fields if f],
        'blank_header_columns': sum(not f for f in fields),
        'missing_required_values': {k: missing[k] for k in sorted(REQUIRED)},
        'status': 'Initial schema and coverage inspection only; duplicate and full quality audit pending.',
    }
    output = ROOT / 'reports' / f'data_inspection_{args.year}_{args.month:02d}.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Inspected {count:,} records, {min(dates)} through {max(dates)}. Saved {output.name}.')


if __name__ == '__main__':
    main()
