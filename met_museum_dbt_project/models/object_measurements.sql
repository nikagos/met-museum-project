SELECT 
    {{ dbt_utils.generate_surrogate_key(['object_id'
                                       , 'measurement_element_name'
                                       , 'measurement_element_description']) }} AS unique_id
  , *
FROM (
        SELECT
            object_id
            , measurements_data->>'elementName' AS measurement_element_name
            , measurements_data->>'elementDescription' AS measurement_element_description
            , MAX(CASE WHEN measurement_key = 'Depth' THEN measurement_value::float END) AS depth
            , MAX(CASE WHEN measurement_key = 'Height' THEN measurement_value::float END) AS height
            , MAX(CASE WHEN measurement_key = 'Width' THEN measurement_value::float END) AS width
        FROM (
                SELECT 
                    "objectID" AS object_id,
                    jsonb_array_elements("measurements"::jsonb) AS measurements_data
                FROM 
                    {{ source('main', 'objects') }}
                WHERE
                    TRUE    
                    -- Exclude rows where the measurements array is [null]
                    AND "measurements" IS NOT NULL
                    AND jsonb_typeof("measurements"::jsonb) = 'array'
                    AND "measurements"::jsonb != '[null]'::jsonb
            ) sq,
        jsonb_each(measurements_data->'elementMeasurements') AS nested_measurements(measurement_key, measurement_value)
        GROUP BY 1,2,3
) sq