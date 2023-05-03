SELECT 
    TrialID,
    Intensity,
    CAST(Outcome AS INT) AS Outcome
FROM {{ source("Simulation", "Trials") }}