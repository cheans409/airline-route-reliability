# U.S. Airline Route Reliability

## January 2025 operations report

Of **539,747 reported flights** in January 2025, **115,608 were cancelled, diverted, or arrived at least 15 minutes late**. Cancellations affected 3.02% of scheduled flights, while 18.79% of eligible arrivals were late. These results establish an initial baseline for identifying routes that warrant closer operational investigation.

This analysis uses official Bureau of Transportation Statistics (BTS) records to address a practical question: **where do substantial flight volumes and reliability problems overlap?** The current report covers January only. Full-year analysis and a Tableau dashboard are planned.

## Reliability across the reporting population

| Measure | January 2025 result |
| --- | ---: |
| Reported scheduled flights | 539,747 |
| Cancelled flights | 16,312 — 3.02% of scheduled flights |
| Diverted flights | 1,166 |
| Eligible arrivals | 522,269 |
| Arrivals at least 15 minutes late | 98,130 — 18.79% of eligible arrivals |
| Total observed disrupted flights | 115,608 |

Eligible arrivals exclude cancellations and diversions and require an observed arrival-delay flag. This distinction matters: cancellation and late-arrival rates describe different populations and should not be added together. The disruption total counts each affected flight once.

All noncancelled, nondiverted flights in this month's data had an observed arrival-delay flag. The results therefore contain no unknown arrival outcomes within that population. [View the monthly results](reports/monthly_summary.csv).

## Routes to investigate first

The initial shortlist ranks carrier-specific directional routes by the **number of disrupted flights**, requiring at least 100 scheduled flights in the month. This emphasizes the scale of disruption while displaying the rate alongside it.

| Carrier code | Route | Scheduled flights | Disrupted flights | Disruption rate |
| --- | --- | ---: | ---: | ---: |
| DL | ATL → MCO | 461 | 157 | 34.06% |
| DL | MCO → ATL | 460 | 134 | 29.13% |
| AA | DFW → SAT | 354 | 129 | 36.44% |
| AS | SEA → ANC | 400 | 127 | 31.75% |

DL's ATL → MCO service had the largest disrupted-flight count among qualifying carrier-routes. Of its 157 disruptions, 143 were late arrivals and 14 were cancellations. The reverse direction also appeared near the top, making this pair a useful starting point for examining whether problems recur across months and departure times.

These are candidates for investigation, not a finding that any particular carrier caused or could have prevented the disruptions. The ranking does not adjust for weather, congestion, schedule mix, or other operating conditions. [View the full preliminary shortlist](reports/priority_routes.csv).

## What the volume threshold changes

A minimum flight count reduces the prominence of very small groups, but also narrows the analysis. At the 100-flight threshold, the comparison includes **1,550 carrier-routes representing 259,445 flights**—less than half of the month's reported flights.

| Minimum monthly flights per carrier-route | Qualifying carrier-routes | Flights represented |
| --- | ---: | ---: |
| 50 | 3,923 | 424,876 |
| 100 | 1,550 | 259,445 |
| 200 | 356 | 94,971 |

The shortlist should therefore be read as a view of busier services, not a complete ranking of the reporting population. These checks measure coverage; stability of the rankings under different thresholds remains to be assessed. [View the threshold comparison](reports/threshold_sensitivity.csv).

## Data and analytical approach

The source is BTS's **Reporting Carrier On-Time Performance** dataset, covering reporting carriers' domestic operations. The January archive contains flight records dated January 1–31, 2025. It does not represent every U.S. operator or flight worldwide. Source files are available through the [official BTS archive](https://www.transtats.bts.gov/PREZIP/), with additional context in the [BTS on-time statistics documentation](https://www.transtats.bts.gov/ot_delay/).

Python validates the archive and prepares records for PostgreSQL. SQL groups flights by month, reporting carrier, origin, and destination, preserving directional routes and keeping cancellations, diversions, and arrival-delay eligibility separate. Airport and carrier IDs are retained alongside their display codes. The [metric definitions](docs/metrics.md) document each denominator.

Source, staging, flight, and aggregated counts all reconcile to 539,747 records. A repeated load preserved that total, and an independent calculation from the source CSV reproduced the monthly counts. Duplicate flight keys and invalid values stop the load rather than silently removing records. Tests cover missing outcomes, cancellation and diversion exclusions, zero eligible-arrival denominators, and duplicate-key rejection. [View the quality checks](reports/load_quality.csv).

## Interpretation and next steps

January provides an initial operational baseline, but one month cannot establish seasonality or persistent underperformance. The analysis measures flights, not affected passengers, route profitability, or avoidable costs. It also does not identify the causes of the observed differences.

The next analytical step is to extend the same definitions across February–December 2025 and test whether the shortlisted routes remain prominent. Comparisons across months, departure times, and carriers serving the same route would help distinguish recurring patterns from isolated periods. A Tableau dashboard will then present the validated results and support further investigation.

## Supporting work

The [SQL analysis](sql/), [January validation report](reports/january_milestone.md), and [source manifest](data/source_manifest.json) provide the evidence behind this report. Planned work is tracked in the [project outline](docs/project_plan.md).
