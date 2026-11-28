-- Exploratory volume-filtered shortlist, not a causal carrier ranking.
-- Change the threshold to 50 or 200 for sensitivity checks.
SELECT * FROM airline.route_month_metrics
WHERE scheduled_flights >= 100
ORDER BY disrupted_flights DESC, observed_disruption_pct DESC,
         month, carrier_id, origin_id, destination_id
LIMIT 20;
