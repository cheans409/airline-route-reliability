# Project plan

## 1. Acquire and audit

Download January 2025 first, then all twelve months. Preserve original archives and checksums. Record schema differences, date coverage, row counts, missing values, cancellations, diversions, and duplicate candidates. Use reporting-carrier data consistently; do not append marketing-carrier records to the same population.

**Acceptance:** twelve documented monthly inputs, coverage verified, and no unexplained duplicate handling or schema mismatches.

## 2. Model in PostgreSQL

Create a raw staging layer that preserves source values and file provenance. Build a typed flight fact table plus airport and carrier dimensions. Use stable DOT carrier IDs and airport IDs where available; retain display codes. Investigate a candidate key using flight date, carrier, flight number, origin, destination, and scheduled departure time before enforcing uniqueness.

**Acceptance:** staging and analytical counts reconcile; rejected rows and conversions are reported; repeat loads do not silently duplicate records.

## 3. Analyze reliability

Produce monthly carrier-route summaries with flight counts, cancellation rates, eligible arrival counts, late-arrival rates, diversions, and positive delay minutes. Compare like routes and months rather than interpreting network-wide rankings as causal carrier effects.

Start with at least 100 scheduled flights per carrier-route-month for ranked displays; check sensitivity at 50 and 200. Show unranked small groups separately. Identify persistence over months and distinguish high rates from high absolute disruption counts.

**Acceptance:** denominators reconcile, missingness is visible, and rankings remain interpretable under alternate volume thresholds.

## 4. Communicate

Build a Tableau dashboard from documented SQL exports. Write a one-page memo with three supported observations, operational questions to investigate, limitations, and next steps. Do not invent savings, passenger impacts, or causal explanations.

**Acceptance:** each displayed metric traces to a query; recommendations cite results; README includes a dashboard preview and quantified findings only after validation.

## Optional extension

Evaluate BTS T-100 domestic segment data for monthly passenger traffic. Document join grain and coverage differences before using it. Aggregate traffic cannot identify passengers on individual delayed flights; any exposure estimate must be explicitly labeled and justified.
