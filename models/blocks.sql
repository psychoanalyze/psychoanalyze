SELECT
    AVG(HitRate) AS avg_HR
FROM {{ ref('points') }}
GROUP BY Intensity
