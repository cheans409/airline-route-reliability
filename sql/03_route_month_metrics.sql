CREATE OR REPLACE VIEW airline.route_month_metrics AS
WITH counts AS (
    SELECT month, carrier_id, carrier_code, origin_id, origin, destination_id, destination,
        count(*) AS scheduled_flights,
        count(*) FILTER (WHERE cancelled) AS cancellations,
        count(*) FILTER (WHERE diverted) AS diversions,
        count(*) FILTER (WHERE NOT cancelled AND NOT diverted AND arrival_late IS NOT NULL) AS eligible_arrivals,
        count(*) FILTER (WHERE NOT cancelled AND NOT diverted AND arrival_late) AS late_arrivals,
        count(*) FILTER (WHERE NOT cancelled AND NOT diverted AND arrival_late IS NULL) AS unknown_arrivals,
        count(*) FILTER (WHERE NOT cancelled AND NOT diverted AND arrival_delay_minutes IS NOT NULL) AS delay_observations,
        sum(arrival_delay_minutes) FILTER (WHERE NOT cancelled AND NOT diverted) AS positive_arrival_delay_minutes,
        count(*) FILTER (WHERE cancelled OR diverted OR arrival_late) AS disrupted_flights
    FROM airline.flights
    GROUP BY month, carrier_id, carrier_code, origin_id, origin, destination_id, destination
)
SELECT *,
    round(100.0*cancellations/scheduled_flights, 2) AS cancellation_pct,
    round(100.0*diversions/scheduled_flights, 2) AS diversion_pct,
    round(100.0*late_arrivals/nullif(eligible_arrivals,0), 2) AS late_arrival_pct,
    round(positive_arrival_delay_minutes/nullif(delay_observations,0), 2) AS mean_positive_arrival_delay_minutes,
    round(100.0*disrupted_flights/scheduled_flights, 2) AS observed_disruption_pct
FROM counts;
-- Month-specific code mappings avoid treating changing codes as permanent IDs.
CREATE OR REPLACE VIEW airline.airports AS
SELECT DISTINCT month, origin_id AS airport_id, origin AS airport_code FROM airline.flights
UNION
SELECT DISTINCT month, destination_id, destination FROM airline.flights;
CREATE OR REPLACE VIEW airline.carriers AS
SELECT DISTINCT month, carrier_id, carrier_code FROM airline.flights;
