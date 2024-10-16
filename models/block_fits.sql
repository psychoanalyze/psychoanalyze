SELECT
    b.BlockID,
    b."Block",
    "Subject",
    FixedIntensity,
    Threshold AS x_0,
    slope AS k,
    "err+" AS UpperConfidenceInterval,
    "err-" AS LowerConfidenceInterval
FROM
    {{ ref("blocks") }} b
