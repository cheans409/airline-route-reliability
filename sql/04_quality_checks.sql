SELECT l.month, l.source_rows,
 (SELECT count(*) FROM airline.staging s WHERE s.month=l.month) AS staged_rows,
 (SELECT count(*) FROM airline.flights f WHERE f.month=l.month) AS fact_rows,
 (SELECT sum(scheduled_flights) FROM airline.route_month_metrics m WHERE m.month=l.month) AS metric_rows,
 (SELECT count(*) FROM airline.flights f WHERE f.month=l.month AND NOT cancelled AND NOT diverted AND arrival_late IS NULL) AS unknown_arrivals,
 (SELECT count(*) FROM airline.flights f WHERE f.month=l.month AND (cancelled OR diverted) AND arrival_late IS NOT NULL) AS excluded_arrival_flags
FROM airline.loads l ORDER BY l.month;
