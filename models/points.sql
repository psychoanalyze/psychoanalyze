SELECT
    COUNT(TrialID) AS n,
    Intensity,
    SUM(Result) AS Hits,
    SUM(Result) / COUNT(TrialID) AS HitRate
FROM {{ ref("trials") }}
GROUP BY Intensity