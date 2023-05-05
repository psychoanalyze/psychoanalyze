{{ config(materialized='external', location='data/test/points.parquet') }}

SELECT
    COUNT(TrialID) AS n,
    Intensity,
    SUM(Result) AS Hits,
    SUM(Result) / COUNT(TrialID) AS HitRate
FROM {{ source("Simulation", "Trials") }}
GROUP BY Intensity