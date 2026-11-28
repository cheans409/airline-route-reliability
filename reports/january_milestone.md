# January 2025: first PostgreSQL milestone

## Implemented

- Checksum-verified ingestion from the official BTS archive into text staging and typed flight facts.
- Atomic replacement of one month, with source-row provenance and database constraints.
- Carrier-route-month metrics with explicit eligibility and missing-value handling.
- Read-only exports of quality checks, monthly totals, a route shortlist, and threshold coverage.

## Initial results

| Measure | January 2025 |
| --- | ---: |
| Reported scheduled flights | 539,747 |
| Cancellations | 16,312 (3.02% of scheduled flights) |
| Diversions | 1,166 |
| Eligible arrivals | 522,269 |
| Arrivals at least 15 minutes late | 98,130 (18.79% of eligible arrivals) |
| Unknown arrival flags among noncancelled, nondiverted flights | 0 |
| Observed disrupted flights | 115,608 |

Source: `monthly_summary.csv`. Cancellations, diversions, and eligible late arrivals are counted once per flight in the disruption total.

Among carrier-routes with at least 100 scheduled flights, DL's ATL → MCO service had the highest disrupted-flight count: 157 of 461 flights (34.06%). That makes it a candidate for investigation, not evidence that its disruptions were avoidable or that it was the worst-performing service after adjusting for operating conditions. The ranking deliberately reflects volume as well as disruption frequency.

## Validation

The initial load and a repeated load both produced 539,747 flight records. Source, staging, fact, and route-metric counts reconcile. The enforced candidate flight key admitted all January rows without duplicates. No rows were silently removed. A separate source-CSV calculation reproduced the monthly counts independently of the SQL aggregation.

Temporary-table tests cover on-time/early arrivals, late arrivals, cancellations, diversions, unknown arrival outcomes, zero eligible denominators, and duplicate-key rejection. Database constraints additionally reject negative positive-delay minutes, contradictory cancellation/diversion flags, and inconsistent arrival flags and delay minutes when both are observed.

## Limits and next milestone

This is one reporting month and a limited reporting-carrier population. It cannot establish seasonality, sustained underperformance, passenger impacts, or cause. The 100-flight threshold retains 1,550 carrier-routes and 259,445 flights; changing the threshold materially changes coverage. The sensitivity export measures coverage, not ranking stability.

Next: acquire February–December, validate consistent coverage, assess ranking stability and persistence, and build the dashboard from the resulting full-year metrics. Stable airport/carrier names and richer dimensions can follow; the current model uses month-specific ID/code mapping views.
