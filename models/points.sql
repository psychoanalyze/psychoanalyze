{{ config(materialized='external', location='data/test/points.parquet') }}

SELECT
    COUNT(TrialID) AS n,
    Intensity,
    SUM(Outcome) AS Hits
FROM {{ ref('trials') }}
GROUP BY Intensity