"""Download an official BTS monthly archive and record its provenance."""
import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=2025)
    parser.add_argument('--month', type=int, choices=range(1, 13), default=1)
    args = parser.parse_args()
    if not 1987 <= args.year <= datetime.now(timezone.utc).year:
        parser.error('year must be between 1987 and the current year')
    name = f'On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{args.year}_{args.month}.zip'
    url = f'https://www.transtats.bts.gov/PREZIP/{name}'
    target = ROOT / 'data/raw' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'AirlineRouteReliability/0.1 (portfolio research)'})
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            partial = Path(temp) / name
            with urllib.request.urlopen(request, timeout=120) as response, partial.open('wb') as output:
                shutil.copyfileobj(response, output)
            with zipfile.ZipFile(partial) as archive:
                if archive.testzip() is not None:
                    raise ValueError('Archive integrity check failed')
            partial.replace(target)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity check failed')
        members = archive.namelist()
    digest = hashlib.sha256()
    with target.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    manifest = ROOT / 'data/source_manifest.json'
    entries = json.loads(manifest.read_text()) if manifest.exists() else {}
    key = f'{args.year}-{args.month:02d}'
    previous = entries.get(key, {})
    entries[key] = {
        'url': url, 'local_path': str(target.relative_to(ROOT)),
        'first_recorded_at_utc': previous.get('first_recorded_at_utc', datetime.now(timezone.utc).isoformat()),
        'sha256': digest.hexdigest(), 'bytes': target.stat().st_size, 'archive_members': members,
    }
    manifest.write_text(json.dumps(entries, indent=2) + '\n')
    print(f'Validated {key}: {target.stat().st_size:,} bytes; manifest saved.')


if __name__ == '__main__':
    main()
