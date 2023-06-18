SELECT
    Day
    ,x_0 AS Threshold
FROM
    {{ ref("block_fits") }}
