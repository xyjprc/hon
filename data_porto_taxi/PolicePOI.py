import json
InputFile = 'porto_portugal.osm2pgsql-geojson/porto_portugal_osm_point.geojson'
entries = []
with open(InputFile, encoding='utf8') as f:
    lines = f.readlines()
    for line in lines:
        j = json.loads(line[:-2])
        if int(j["properties"]['osm_id']) in set([441813228, 2179762595, 4754437409, 1769415200, 2052784174, 691345709, 2083944955, 2341053579, 4581763228, 1223740133, 1239645069, 2410319697, 2410334466, 1890425072, 1723737220, 4554544641, 4568640016, 473890410, 1198781146, 2530784036, 2454698483, 915484644, 2791603137, 708285559, 688007305, 1187121688, 1854154069, 453466927, 2041648981, 4133988597, 1244643577, 1244643586, 3143576056, 3143576055, 4019669642, 595656117, 595656386, 4568019581, 4151903110, 1489725386, 2044759128]):
            name = j['properties']['name']
            lat = j['geometry']['coordinates'][0]
            lon = j['geometry']['coordinates'][1]
            entries.append((lat, lon, name))

with open('PoliceCoords.csv', 'w', encoding='utf8') as f:
    for entry in entries:
        f.write(','.join([str(x) for x in entry]) + '\n')
