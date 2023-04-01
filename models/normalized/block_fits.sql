SELECT
    BlockID,
    Threshold,
    "err+" AS UpperConfidenceInterval,
    "err-" AS LowerConfidenceInterval
FROM
    'data/fit.csv'