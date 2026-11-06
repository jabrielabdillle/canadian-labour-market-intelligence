WITH unemployment AS (
    SELECT month, geography, rate
    FROM rates
    WHERE metric = 'Unemployment rate' AND rate IS NOT NULL
), latest AS (
    SELECT MAX(month) AS month FROM unemployment WHERE geography = 'Canada'
)
SELECT current.month, current.geography, current.rate AS unemployment_pct,
       ROUND(current.rate - previous.rate, 2) AS yoy_change_pp,
       ROUND(current.rate - national.rate, 2) AS gap_vs_canada_pp,
       DENSE_RANK() OVER (ORDER BY current.rate DESC) AS provincial_rank
FROM unemployment AS current
JOIN latest ON current.month = latest.month
JOIN unemployment AS national
  ON national.month = current.month AND national.geography = 'Canada'
LEFT JOIN unemployment AS previous
  ON previous.geography = current.geography
 AND previous.month = DATE(current.month, '-1 year')
WHERE current.geography <> 'Canada'
ORDER BY provincial_rank, current.geography;
