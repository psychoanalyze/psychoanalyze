SELECT
    x_0 as Threshold
    ,FixedIntensity
FROM {{ ref('block_fits') }}
