SELECT DISTINCT
    "objectID" AS object_id
    , "isHighlight" AS is_highlight
    , "accessionNumber" AS accession_number
    , "accessionYear" AS accession_year
    , "isPublicDomain" AS is_public_domain
    , "primaryImage" AS primary_image
    , "primaryImageSmall" AS primary_image_small
    , "additionalImages" AS addiational_image
    , department
    , "objectName" AS object_name
    , title
    , culture
    , period
    , dynasty
    , reign
    , portfolio
    , "artistRole" AS artist_role
    , "artistPrefix" AS artist_prefix
    , "artistDisplayName" AS artist_display_name
    , "artistDisplayBio" AS artist_display_bio
    , "artistSuffix" AS artist_suffix
    , "artistAlphaSort" AS artist_alpha_sort
    , "artistNationality" AS artist_nationality
    , "artistBeginDate" AS artist_begin_date
    , "artistEndDate" AS artist_end_date
    , "artistGender" AS artist_gender
    , "artistWikidata_URL" AS artist_wikidata_url
    , "artistULAN_URL" AS artist_ulan_url
    , "objectDate" AS object_date
    , "objectBeginDate" AS object_begin_date
    , "objectEndDate" AS object_end_date
    , medium
    , dimensions
    , "creditLine" AS credit_line
    , "geographyType" AS geography_type
    , city
    , state
    , county
    , country
    , region
    , subregion
    , locale
    , locus
    , excavation
    , river
    , classification
    , "rightsAndReproduction" AS rights_and_reproduction
    , "linkResource" AS link_resource
    , "metadataDate" AS metadata_date
    , repository
    , "objectURL" AS object_url
    , tags::jsonb AS tags
    , "objectWikidata_URL" AS object_wikidata_url
    , "isTimelineWork" AS is_timeline_work
    , "GalleryNumber" AS gallery_number
FROM
    {{ source('main', 'objects') }} o
LEFT JOIN
    {{ ref('object_measurements') }} om
ON
    o."objectID" = om.object_id