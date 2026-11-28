"""Database-backed edge cases; uses temporary tables, never edits project records."""
import os
import unittest
from pathlib import Path
import psycopg2

ROOT = Path(__file__).resolve().parents[1]


class MetricsTest(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with psycopg2.connect(os.environ.get('DATABASE_URL', 'dbname=airline_reliability')) as conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TEMP TABLE duplicate_fixture (LIKE airline.flights INCLUDING ALL)')
                cur.execute('INSERT INTO duplicate_fixture SELECT * FROM airline.flights LIMIT 1')
                self.assertEqual(cur.rowcount, 1)
                cur.execute('SAVEPOINT duplicate_attempt')
                with self.assertRaises(psycopg2.errors.UniqueViolation):
                    cur.execute('INSERT INTO duplicate_fixture SELECT * FROM duplicate_fixture')
                cur.execute('ROLLBACK TO SAVEPOINT duplicate_attempt')
                cur.execute('SELECT count(*) FROM duplicate_fixture')
                self.assertEqual(cur.fetchone()[0], 1)

    def test_denominators_and_unknown_outcomes(self):
        with psycopg2.connect(os.environ.get('DATABASE_URL', 'dbname=airline_reliability')) as conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TEMP TABLE fixture_flights (LIKE airline.flights)')
                cases = [(False, False, False, 0), (False, False, True, 30),
                         (True, False, None, None), (False, True, None, None),
                         (False, False, None, None), (False, False, False, 0)]
                for i, flags in enumerate(cases, 1):
                    cur.execute('''INSERT INTO fixture_flights VALUES
                        ('2025-01-01',%s,'2025-01-01',1,'AA',%s,1,'AAA',2,'BBB','1200',%s,%s,%s,%s)''',
                        (i, str(i), *flags))
                # Separate route with no eligible arrivals tests division by zero.
                cur.execute('''INSERT INTO fixture_flights VALUES
                    ('2025-01-01',7,'2025-01-01',1,'AA','7',1,'AAA',3,'CCC','1200',true,false,NULL,NULL)''')
                sql = (ROOT / 'sql/03_route_month_metrics.sql').read_text().split('-- Month-specific')[0]
                sql = sql.replace('CREATE OR REPLACE VIEW airline.route_month_metrics', 'CREATE TEMP VIEW fixture_metrics')
                cur.execute(sql.replace('airline.flights', 'fixture_flights'))
                cur.execute('''SELECT scheduled_flights,cancellations,diversions,eligible_arrivals,
                    late_arrivals,unknown_arrivals,delay_observations,disrupted_flights,
                    late_arrival_pct,mean_positive_arrival_delay_minutes
                    FROM fixture_metrics WHERE destination='BBB' ''')
                row = cur.fetchone()
                self.assertEqual(row[:8], (6,1,1,3,1,1,3,3))
                self.assertEqual(str(row[8]), '33.33')
                self.assertEqual(row[9], 10)
                cur.execute("SELECT late_arrival_pct,mean_positive_arrival_delay_minutes FROM fixture_metrics WHERE destination='CCC'")
                self.assertEqual(cur.fetchone(), (None,None))


if __name__ == '__main__':
    unittest.main()
