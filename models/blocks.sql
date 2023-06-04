SELECT
    AVG(HitRate) AS avg_HR
FROM {{ ref('points') }}
GROUP BY
    Monkey
    ,Date
    ,Amp2
    ,Width2
    ,Freq2
    ,Dur2
    ,ActiveChannels
    ,ReturnChannels
