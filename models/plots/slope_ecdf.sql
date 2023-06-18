SELECT
    k
    ,Subject
FROM {{ ref('block_fits') }}
