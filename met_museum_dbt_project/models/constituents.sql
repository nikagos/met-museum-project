SELECT 
        {{ dbt_utils.generate_surrogate_key(['object_id'
                                           , 'constituent_id']) }} AS unique_id
      , *  
FROM (
        SELECT
            "objectID" AS object_id
          , jsonb_array_elements("constituents"::jsonb)->>'constituentID' AS constituent_id
          , jsonb_array_elements("constituents"::jsonb)->>'role' AS constituent_role
          , jsonb_array_elements("constituents"::jsonb)->>'name' AS constituent_name
          , jsonb_array_elements("constituents"::jsonb)->>'constituentULAN_URL' AS constituent_ulan_url
          , jsonb_array_elements("constituents"::jsonb)->>'constituentWikidata_URL' AS constituent_wikidata_url
          , jsonb_array_elements("constituents"::jsonb)->>'gender' AS constituent_gender
        FROM
            {{ source('main', 'objects') }}
        GROUP BY
            1,2,3,4,5,6,7
    ) sq