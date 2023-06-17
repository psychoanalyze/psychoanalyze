SELECT
    Subject
    ,BlockID
    ,TrialID
    ,Result
FROM {{ source("Schlichenmeyer2022", "Trials") }}
