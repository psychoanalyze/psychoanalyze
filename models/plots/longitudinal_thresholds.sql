SELECT
    s.Day,
    fits.Threshold,
    fits.UpperConfidenceInterval,
    fits.LowerConfidenceInterval
FROM {{ ref('sessions') }} s
    INNER JOIN {{ ref('blocks') }} b
        ON b.SessionID = s.SessionID
    INNER JOIN {{ ref('block_fits') }} fits
        ON fits.BlockID = b.BlockID