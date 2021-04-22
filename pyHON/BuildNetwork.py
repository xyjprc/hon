'''
This version resolved the count issues after rewiring for freq mode.
e.g. if a->b has been changed as a->b|a, then count[b][*]-=count[b|a][*]
if a|q->b has been changed as a|q->b|a, then count[b][*]-=count[b|a][*]
'''


from collections import defaultdict, Counter

Graph = defaultdict(dict)
Verbose = True

def Initialize():
    Graph = defaultdict(dict)


def BuildNetwork(Rules):
    VPrint('Building network')
    # Initialize()
    Graph.clear()
    SortedSource = sorted(Rules, key=lambda x: len(x))
    ToAdd = []
    ToRemove = []
    for source in SortedSource:
        for target in Rules[source]:
            Graph[source][(target,)] = Rules[source][target]
            # following operations are destructive to Rules
            if len(source) > 1:
                Rewire(source, (target,), ToAdd, ToRemove)
    for (source, target, weight) in ToAdd:
        Graph[source][target] = weight
    for (source, target) in ToRemove:
        del(Graph[source][target])
    RewireTails()
    return Graph

def Rewire(source, target, ToAdd, ToRemove):
    PrevSource = source[:-1]
    PrevTarget = (source[-1],)
    if not PrevSource in Graph or not source in Graph[PrevSource]:
        if (PrevSource, source, Graph[PrevSource][PrevTarget]) not in ToAdd:
            ToAdd.append((PrevSource, source, Graph[PrevSource][PrevTarget]))
        if (PrevSource, PrevTarget) not in ToRemove:
            ToRemove.append((PrevSource, PrevTarget))
        # remove the counts for the wired nodes
        # e.g. if a->b has been changed as a->b|a, then count[b][*]-=count[b|a][*]
        if target in Graph[PrevTarget]:
            Graph[PrevTarget][target] -= Graph[source][target]
            if Graph[PrevTarget][target] == 0:
                del(Graph[PrevTarget][target])

def RewireTails():
    ToAdd = []
    ToRemove = []
    ToReduce = []
    for source in Graph:
        for target in Graph[source]:
            if len(target) == 1:
                NewTarget = source + target
                while len(NewTarget) > 1:
                    if NewTarget in Graph:
                        ToAdd.append((source, NewTarget, Graph[source][target]))
                        ToRemove.append((source, target))
                        ToReduce.append((target, NewTarget))
                        break
                    else:
                        NewTarget = NewTarget[1:]
    for (source, target, weight) in ToAdd:
        Graph[source][target] = weight
    for (source, target) in ToRemove:
        del(Graph[source][target])
    # reduce the counts for the retailed nodes
    # e.g. if a|q->b has been changed as a|q->b|a, then count[b][*]-=count[b|a][*]
    for (target, NewTarget) in ToReduce:
        for NextStep in Graph[NewTarget]:
            if NextStep in Graph[target]:
                Graph[target][NextStep] -= Graph[NewTarget][NextStep]
                if Graph[target][NextStep] == 0:
                    del(Graph[target][NextStep])


###########################################
# Auxiliary functions
###########################################

def VPrint(string):
    if Verbose:
        print(string)
