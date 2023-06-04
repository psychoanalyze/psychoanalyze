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
    ,TrialID
    ,Result
FROM {{ source("Schlichenmeyer2022", "Trials") }}