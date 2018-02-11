from collections import defaultdict
import datetime
from datetime import date
import csv

InputData = './train.csv'
POIdata = 'PoliceCoords.csv'

trips = defaultdict(lambda: defaultdict(list))

###########################


def PolylineToGrid(polyline):
    #print(polyline)
    vals = []
    polyline = polyline.split(']')
    for pair in polyline:
        #print(pair)
        p = pair
        if len(p) < 2:
            continue
        if pair[0] == ',':
            p = pair[2:]
        left = float(p.split(',')[0].replace('[', '').replace(']', ''))
        right = float(p.split(',')[1].replace('[', '').replace(']', ''))

        if -9 < left < -8 and 40 < right < 42:

            vals.append(CoordToPOI(left, right))
    return vals


def CoordToPOI(left, right):
    min = 999
    closest = -1
    for pleft, pright in POI:
        distance = (pleft-left)**2 + (pright-right)**2
        if distance < min:
            closest = POI[(pleft, pright)]
            min = distance
    return str(closest)
##########################
##########################

POI = {}
PoiId = 1
with open(POIdata) as f:
    for line in f:
        fields = line.strip().split(',')
        lat, lon, name = fields
        POI[(float(lat), float(lon))] = str(PoiId)
        PoiId += 1


DateTaxiPoly = []
with open(InputData, newline='') as f:
    counter = 0
    reader = csv.reader(f)
    next(f)
    for row in reader:
        counter += 1
        if counter % 10000 == 0:
            print(counter)
        TRIP_ID,CALL_TYPE,ORIGIN_CALL,ORIGIN_STAND,TAXI_ID,TIMESTAMP,DAY_TYPE,MISSING_DATA,POLYLINE=row
        DateTaxiPoly.append((TIMESTAMP, (TAXI_ID, POLYLINE)))
print('raw data')

DateTaxiPoly.sort()
print('sorted')

counter = 0
for line in DateTaxiPoly:
    counter += 1
    if counter % 10000 == 0:
        print(counter)
    TIMESTAMP = line[0]
    TAXI_ID, POLYLINE = line[1]
    TripDate = datetime.datetime.utcfromtimestamp(int(TIMESTAMP)).date()
    TripWeek = (TripDate-date(2013,6,30)).days//7
    trips[TripWeek][TAXI_ID].extend(PolylineToGrid(POLYLINE))
print('cleaned')

for TripWeek in trips:
    with open('trajectories/'+ str(TripWeek) +'.csv', 'w') as f:
        print(TripWeek)
        for TAXI_ID in trips[TripWeek]:
            f.write(TAXI_ID + ' ' + ' '.join(trips[TripWeek][TAXI_ID]) + '\n')

print('done')
