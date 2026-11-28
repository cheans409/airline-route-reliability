CREATE SCHEMA IF NOT EXISTS airline;
CREATE TABLE IF NOT EXISTS airline.loads (
    month date PRIMARY KEY CHECK (extract(day FROM month)=1),
    source_file text NOT NULL, sha256 text NOT NULL,
    source_rows integer NOT NULL CHECK (source_rows > 0),
    loaded_at timestamptz NOT NULL DEFAULT now()
);
-- Raw analytical fields stay as text; complete original records remain in the ZIP.
CREATE TABLE IF NOT EXISTS airline.staging (
    month date NOT NULL REFERENCES airline.loads ON DELETE CASCADE,
    source_row integer NOT NULL,
    flight_date text, carrier_id text, carrier_code text, flight_number text,
    origin_id text, origin text, destination_id text, destination text,
    scheduled_departure text, cancelled text, diverted text,
    arrival_late text, arrival_delay_minutes text,
    PRIMARY KEY (month, source_row)
);
CREATE TABLE IF NOT EXISTS airline.flights (
    month date NOT NULL REFERENCES airline.loads ON DELETE CASCADE,
    source_row integer NOT NULL,
    flight_date date NOT NULL, carrier_id integer NOT NULL, carrier_code text NOT NULL,
    flight_number text NOT NULL, origin_id integer NOT NULL, origin text NOT NULL,
    destination_id integer NOT NULL, destination text NOT NULL,
    scheduled_departure text NOT NULL,
    cancelled boolean NOT NULL, diverted boolean NOT NULL,
    arrival_late boolean, arrival_delay_minutes numeric CHECK (arrival_delay_minutes >= 0),
    PRIMARY KEY (month, source_row),
    UNIQUE (flight_date, carrier_id, flight_number, origin_id, destination_id, scheduled_departure),
    CHECK (date_trunc('month', flight_date)::date = month),
    CHECK (NOT (cancelled AND diverted)),
    CHECK (arrival_late IS NULL OR arrival_delay_minutes IS NULL OR
           arrival_late = (arrival_delay_minutes >= 15))
);
