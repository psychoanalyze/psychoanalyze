SELECT
    Day
    ,Subject
    ,FixedIntensity
    ,TrialID
    ,Intensity
    ,Result
FROM {{ source("Schlichenmeyer2022", "Trials") }}