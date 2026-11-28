# SQL execution order

The loader executes `01_schema.sql`, `02_transform.sql`, and `03_route_month_metrics.sql` inside one transaction. The transformation file takes a Python database parameter for the selected month; run it through `scripts/load_postgres.py`.

- `01_schema.sql`: load provenance, raw analytical fields, typed flight facts, and constraints.
- `02_transform.sql`: typed monthly insertion; duplicates fail the entire transaction.
- `03_route_month_metrics.sql`: carrier-route-month metrics and monthly airport/carrier mapping views.
- `04_quality_checks.sql`: source/staging/fact/aggregate reconciliation and missing/excluded arrival flags.
- `05_priority_routes.sql`: preliminary top 20 by disrupted flight count, requiring at least 100 scheduled flights.

The last two files can also run directly in a PostgreSQL client. `scripts/export_results.py` exports them alongside monthly totals and 50/100/200-flight threshold coverage checks in a consistent read-only database snapshot. Those threshold checks describe coverage changes, not full ranking stability.
