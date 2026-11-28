-- Run inside the loader transaction for its selected month.
INSERT INTO airline.flights
SELECT month, source_row, flight_date::date, carrier_id::integer, carrier_code,
       flight_number, origin_id::integer, origin, destination_id::integer, destination,
       scheduled_departure,
       cancelled::numeric = 1, diverted::numeric = 1,
       nullif(arrival_late, '')::numeric = 1,
       nullif(arrival_delay_minutes, '')::numeric
FROM airline.staging WHERE month = %(month)s;
