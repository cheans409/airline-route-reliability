"""Atomically replace one month; fail on invalid records or duplicate flight keys."""
import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['FlightDate', 'DOT_ID_Reporting_Airline', 'Reporting_Airline',
          'Flight_Number_Reporting_Airline', 'OriginAirportID', 'Origin',
          'DestAirportID', 'Dest', 'CRSDepTime', 'Cancelled', 'Diverted',
          'ArrDel15', 'ArrDelayMinutes']


def prepare(archive_path, month, output):
    count = 0
    with zipfile.ZipFile(archive_path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(members) != 1:
            raise ValueError('Expected one CSV')
        with archive.open(members[0]) as source:
            reader = csv.DictReader(io.TextIOWrapper(source, encoding='utf-8-sig'))
            if not set(FIELDS).issubset(reader.fieldnames or []):
                raise ValueError('Required source fields missing')
            writer = csv.writer(output)
            for count, row in enumerate(reader, 1):
                observed = date.fromisoformat(row['FlightDate'])
                if observed.replace(day=1) != month:
                    raise ValueError(f'Out-of-month record at source row {count}')
                for field in FIELDS[:11]:
                    if not row[field].strip():
                        raise ValueError(f'Missing {field} at row {count}')
                for flag in ['Cancelled', 'Diverted', 'ArrDel15']:
                    allowed = {'0.00', '1.00', '0', '1'}
                    if flag == 'ArrDel15':
                        allowed.add('')
                    if row[flag] not in allowed:
                        raise ValueError(f'Invalid {flag} at row {count}')
                writer.writerow([month.isoformat(), count] + [row[k] for k in FIELDS])
    if not count:
        raise ValueError('Empty input')
    output.seek(0)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=2025)
    parser.add_argument('--month', type=int, choices=range(1, 13), default=1)
    args = parser.parse_args()
    month = date(args.year, args.month, 1)
    key = f'{args.year}-{args.month:02d}'
    manifest = json.loads((ROOT / 'data/source_manifest.json').read_text())[key]
    path = ROOT / manifest['local_path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest['sha256']:
        raise ValueError('Archive checksum differs from source manifest')
    # Validate and stage locally before touching the database.
    with tempfile.TemporaryFile(mode='w+', newline='') as prepared:
        count = prepare(path, month, prepared)
        with psycopg2.connect(os.environ.get('DATABASE_URL', 'dbname=airline_reliability')) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT pg_advisory_xact_lock(20250127)')
                cur.execute((ROOT / 'sql/01_schema.sql').read_text())
                cur.execute('DELETE FROM airline.loads WHERE month=%s', (month,))
                cur.execute('INSERT INTO airline.loads(month,source_file,sha256,source_rows) VALUES (%s,%s,%s,%s)',
                            (month, str(path.relative_to(ROOT)), digest, count))
                cur.copy_expert('COPY airline.staging FROM STDIN WITH (FORMAT CSV)', prepared)
                cur.execute((ROOT / 'sql/02_transform.sql').read_text(), {'month': month})
                if cur.rowcount != count:
                    raise ValueError('Transformed row count mismatch')
                cur.execute((ROOT / 'sql/03_route_month_metrics.sql').read_text())
                cur.execute('SELECT sum(scheduled_flights), sum(cancellations+diversions+eligible_arrivals+unknown_arrivals) FROM airline.route_month_metrics WHERE month=%s', (month,))
                if tuple(cur.fetchone()) != (count, count):
                    raise ValueError('Metric reconciliation failed')
        print(f'Committed {count:,} records for {key}; source, fact, and metric counts reconcile.')


if __name__ == '__main__':
    main()
