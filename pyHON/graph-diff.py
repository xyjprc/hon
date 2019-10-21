# computes diff of neighboring static graphs of a dynamic graph,
# and plot the diff scores

# Note: this file (implements the weight difference)
# serves as an example of how graph differences can be computed.
# Network differences can be computed in many other ways (max common subgraph, etc)
# The code won't run out of the box (it was written a long time ago; some paths need to be updated).
# Still, hope this snippet can be helpful.

import matplotlib.pyplot as plt
import glob
import pprint
import datetime

filetype = 'bayesian-firstorder-10'
k = 7
NoWeekends = False

NetworkPath = '../data/NYC-' + filetype + '-network/*'
filetype = filetype + '-k' + str(k)
if NoWeekends:
    filetype = filetype + '-NoWeekends'


fn = glob.glob(NetworkPath)
fncleaned = []
if NoWeekends:
    for f in fn:
        date = f.strip().split('\\')[-1].split('.')[0]
        month, day = date.split('_')
        time = datetime.date(2013, int(month), int(day))
        if time.isoweekday() < 6:
            fncleaned.append(f)
    fn = fncleaned[:]
fn = sorted(fn)
print(fn)
pairs = list(zip(fn[:-k], fn[k:]))
distances = []


for pair in pairs:
    fileG = pair[0]
    fileH = pair[1]
    print(fileG)
    distance = 0
    AllEdges = set()
    GEdges = {}
    HEdges = {}
    GEdgesSet = set()
    HEdgesSet = set()
    VerboseDistances = []
    with open(fileG) as FG:
        with open(fileH) as FH:
            for line in FG:
                fields = line.split(',')
                FromNode = fields[0]
                ToNode = fields[1]
                weight = float(fields[2].strip())
                GEdges[(FromNode, ToNode)] = weight
                GEdgesSet.add((FromNode, ToNode))
            for line in FH:
                fields = line.split(',')
                FromNode = fields[0]
                ToNode = fields[1]
                weight = float(fields[2].strip())
                HEdges[(FromNode, ToNode)] = weight
                HEdgesSet.add((FromNode, ToNode))
    # edges as the union of the two graphs
    AllEdges = GEdgesSet | HEdgesSet
    for edge in AllEdges:
        if edge in GEdges:
            GWeight = GEdges[edge]
        else:
            GWeight = 0
        if edge in HEdges:
            HWeight = HEdges[edge]
        else:
            HWeight = 0
        #print(GWeight, HWeight, abs(GWeight - HWeight) / max(GWeight, HWeight))
        value = abs(GWeight - HWeight) / max(GWeight, HWeight)
        distance += value
        VerboseDistances.append((value, edge, GWeight, HWeight))
    distance /= len(AllEdges)
    distances.append(distance)
    #pprint.pprint(sorted(VerboseDistances, reverse=True)[:10])
print(distances)
#plt.clf()
plt.plot(distances)
plt.savefig('../figs/NYC-'+filetype+'.png')
with open('../data/NYC-'+filetype+'-distances.csv', 'w') as f:
    for distance in distances:
        f.write(str(distance) + '\n')
