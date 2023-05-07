SELECT
    BlockID,
    "Day",
    "Subject",
    FixedIntensity,
    Threshold AS x_0,
    slope AS k,
    "err+" AS UpperConfidenceInterval,
    "err-" AS LowerConfidenceInterval
FROM
    'data/fit.csv'