# SQL implementation plan

Queries will be added after source validation:

1. `01_schema.sql`: raw staging, typed flight records, airport and carrier dimensions.
2. `02_quality_checks.sql`: coverage, duplicate candidates, missing values, flag consistency, and load reconciliation.
3. `03_route_month_metrics.sql`: carrier-route-month numerators and denominators.
4. `04_priority_routes.sql`: volume-filtered comparisons and persistence across months.
5. `05_dashboard_exports.sql`: documented tables for Tableau.

These are planned deliverables, not existing runnable SQL files. See `docs/metrics.md` for metric definitions.
