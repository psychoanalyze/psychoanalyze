SELECT
    Subject
    ,BlockID
    ,COUNT(TrialID) AS n
    ,SUM(Result) AS Hits
    ,SUM(Result) / COUNT(TrialID) AS HitRate
FROM {{ ref("trials") }}
GROUP BY
    Subject
    ,BlockID
