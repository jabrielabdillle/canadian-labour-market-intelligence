CREATE TABLE rates (
    month TEXT NOT NULL,
    geography TEXT NOT NULL,
    metric TEXT NOT NULL,
    rate REAL CHECK (rate BETWEEN 0 AND 100),
    status TEXT NOT NULL,
    source_vector TEXT NOT NULL,
    PRIMARY KEY (month, geography, metric)
);
CREATE INDEX rates_series ON rates (metric, geography, month);
