SELECT
    Monkey
    ,Date
    ,Amp2
    ,Width2
    ,Freq2
    ,Dur2
    ,ActiveChannels
    ,ReturnChannels
    ,Amp1
    ,Width1
    ,Freq1
    ,Dur1
    ,COUNT(TrialID) AS n
    ,SUM(Result) AS Hits
    ,SUM(Result) / COUNT(TrialID) AS HitRate
FROM {{ ref("trials") }}
GROUP BY
    Monkey
    ,Date
    ,Amp2
    ,Width2
    ,Freq2
    ,Dur2
    ,ActiveChannels
    ,ReturnChannels
    ,Amp1
    ,Width1
    ,Freq1
    ,Dur1