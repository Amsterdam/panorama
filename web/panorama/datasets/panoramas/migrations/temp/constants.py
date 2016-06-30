SQL_VIEW_0002 = """
SELECT
    ROW_NUMBER() over (order by pp.id) as id,
    pp.id as from_pano_id,
    pp1.id as to_pano_id,
    degrees(ST_Azimuth(geography(pp.geolocation), geography(pp1.geolocation))) as direction,
    ST_Distance(geography(pp.geolocation), geography(pp1.geolocation)) as distance,
    ST_Z(pp.geolocation) as from_height,
    ST_Z(pp1.geolocation) as to_height
FROM
    panoramas_panorama pp,
    panoramas_panorama pp1
WHERE
    ST_DWithin(geography(pp.geolocation), geography(pp1.geolocation), 10)
AND
    pp1.id <> pp.id
ORDER BY from_pano_id, to_pano_id"""
SQL_VIEWNAME_0002 = "panoramas_adjacency"
