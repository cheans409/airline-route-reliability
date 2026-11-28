"""Export auditable database summaries; no raw flight records are published."""
import csv
import os
from pathlib import Path
import psycopg2

ROOT = Path(__file__).resolve().parents[1]
QUERIES = {
    'load_quality.csv': (ROOT / 'sql/04_quality_checks.sql').read_text(),
    'priority_routes.csv': (ROOT / 'sql/05_priority_routes.sql').read_text(),
    'monthly_summary.csv': '''SELECT month,sum(scheduled_flights) AS scheduled_flights,
        sum(cancellations) AS cancellations,sum(diversions) AS diversions,
        sum(eligible_arrivals) AS eligible_arrivals,sum(late_arrivals) AS late_arrivals,
        sum(unknown_arrivals) AS unknown_arrivals,sum(disrupted_flights) AS disrupted_flights,
        round(100.0*sum(cancellations)/sum(scheduled_flights),2) AS cancellation_pct,
        round(100.0*sum(late_arrivals)/nullif(sum(eligible_arrivals),0),2) AS late_arrival_pct
        FROM airline.route_month_metrics GROUP BY month ORDER BY month''',
    'threshold_sensitivity.csv': '''SELECT month,t.threshold,count(*) AS eligible_carrier_routes,
        sum(scheduled_flights) AS covered_flights,sum(disrupted_flights) AS disrupted_flights
        FROM airline.route_month_metrics CROSS JOIN (VALUES (50),(100),(200)) t(threshold)
        WHERE scheduled_flights >= t.threshold GROUP BY month,t.threshold ORDER BY month,t.threshold''',
}


def main():
    with psycopg2.connect(os.environ.get('DATABASE_URL', 'dbname=airline_reliability')) as conn:
        conn.set_session(readonly=True, isolation_level='REPEATABLE READ')
        with conn.cursor() as cur:
            for name, query in QUERIES.items():
                cur.execute(query)
                with (ROOT / 'reports' / name).open('w', newline='') as output:
                    writer = csv.writer(output)
                    writer.writerow([column.name for column in cur.description])
                    writer.writerows(cur)
                print(f'Exported reports/{name}')


if __name__ == '__main__':
    main()
