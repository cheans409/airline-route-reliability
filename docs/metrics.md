# Proposed metric contract

These definitions will be validated against the downloaded schema before analysis.

| Metric | Numerator | Denominator / eligibility |
| --- | --- | --- |
| Scheduled reported flights | Count of source flight records after validated duplicate handling | All included records; not all U.S. flights |
| Cancellation rate | Records with Cancelled = 1 | All included scheduled records |
| Diversion rate | Records with Diverted = 1 | All included scheduled records |
| Late-arrival rate | Eligible records with ArrDel15 = 1 | Noncancelled, nondiverted records with observed ArrDel15 |
| Mean positive arrival delay | Sum of ArrDelayMinutes | Noncancelled, nondiverted records with observed ArrDelayMinutes; includes zero-delay arrivals |
| Observed disrupted flights | Cancelled OR diverted OR eligible late arrival | Count each record at most once; report unknown arrival outcomes separately |

- Late arrival uses the BTS 15-minute threshold. Early arrivals must not offset late minutes in the positive-delay metric.
- Report missing arrival outcomes rather than replacing them with on-time outcomes.
- Keep cancellations and diversions separate from arrival-delay denominators.
- Route means ordered origin–destination; carrier-route-month is the initial comparison grain.
- For an overall rate, divide summed numerators by summed eligible denominators. Do not average monthly percentages unweighted.
- Delay-cause fields have conditional reporting coverage; missing values are not automatically zero and do not establish causation.
- Rank rates alongside volume. Do not create an arbitrary weighted score before inspecting the distributions.
