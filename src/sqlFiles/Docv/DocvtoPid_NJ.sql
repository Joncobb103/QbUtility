SELECT * FROM developer.docv dv 
left join billy.depvalld dp on dp.id = dv.deposit_id 
join developer.rocrv r on dp.id = r.deposit_id 
where dp.state = 'NJ' and dp.deposit_date = '(REPLACE DATE)' 
and dp.district_full_name IN (
'ASBURY PARK (MONMOUTH, NJ)'
,'BARNEGAT (OCEAN, NJ)'
,'BRIDGETON (CUMBERLAND, NJ)'
,'BURLINGTON (BURLINGTON, NJ)'
,'CAMDEN CITY (CAMDEN, NJ)'
,'CARNEYS POINT (SALEM, NJ)'
,'CARTERET (MIDDLESEX, NJ)'
,'CLIFTON (PASSAIC, NJ)'
,'EAST BRUNSWICK (MIDDLESEX, NJ)'
,'EAST ORANGE (ESSEX, NJ)'
,'EGG HARBOR (ATLANTIC, NJ)'
,'EVESHAM (BURLINGTON, NJ)'
,'GALLOWAY (ATLANTIC, NJ)'
,'GLOUCESTER TOWNSHIP (CAMDEN, NJ)'
,'HAMILTON (MERCER, NJ)'
,'HAZLET (MONMOUTH, NJ)'
,'HIGHLANDS (MONMOUTH, NJ)'
,'HILLSBOROUGH (SOMERSET, NJ)'
,'HILLSIDE (UNION, NJ)'
,'HOPATCONG (SUSSEX, NJ)'
,'JACKSON (OCEAN, NJ)'
,'KEANSBURG (MONMOUTH, NJ)'
,'LACEY (OCEAN, NJ)'
,'LAKEWOOD (OCEAN, NJ)'
,'LINDEN (UNION, NJ)2'
,'LINDEN (UNION, NJ)'
,'LINDENWOLD (CAMDEN, NJ)'
,'LONG BRANCH (MONMOUTH, NJ)'
,'MAPLEWOOD (ESSEX, NJ)'
,'MARLBORO (MONMOUTH, NJ)'
,'MATAWAN (MONMOUTH, NJ)'
,'MEDFORD (BURLINGTON, NJ)'
,'MIDDLE TOWNSHIP (CAPE MAY, NJ)'
,'MILLVILLE (CUMBERLAND, NJ)'
,'NEPTUNE TOWNSHIP (MONMOUTH, NJ)'
,'NEWARK (ESSEX, NJ)'
,'NORTH PLAINFIELD (SOMERSET, NJ)'
,'OCEAN (MONMOUTH, NJ)'
,'OCEAN (OCEAN, NJ)'
,'OXFORD (WARREN, NJ)'
,'PASSAIC (PASSAIC, NJ)'
,'PATERSON (PASSAIC, NJ)'
,'PAULSBORO (GLOUCESTER, NJ)'
,'PENNS GROVE (SALEM, NJ)'
,'PEQUANNOCK (MORRIS, NJ)'
,'PISCATAWAY (MIDDLESEX, NJ)'
,'PLEASANTVILLE (ATLANTIC, NJ)'
,'POINT PLEASANT (OCEAN, NJ)'
,'ROCKAWAY TOWNSHIP (MORRIS, NJ)'
,'TEANECK (BERGEN, NJ)'
,'TOMS RIVER (OCEAN, NJ)'
,'TRENTON (MERCER, NJ)'
,'TUCKERTON (OCEAN, NJ)'
,'UNION CITY (HUDSON, NJ)'
,'VINELAND (CUMBERLAND, NJ)'
,'WASHINGTON (GLOUCESTER, NJ)'
,'WILLINGBORO (BURLINGTON, NJ)'
,'WINSLOW (CAMDEN, NJ)'
) 
and r.ocr_text is null

;