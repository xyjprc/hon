### Major update: parameter free and magnitudes faster than previous versions.
### Paper and pseudocode: https://arxiv.org/abs/1712.09658


### This file: line-by-line translation from Algorithm 1
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Apr 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/xyjprc/hon

### Call ExtractRules()
### Input: Trajectory
### Output: Higher-order dependency rules
### See details in README

from collections import defaultdict, Counter
#from concurrent import futures

import math

ThresholdMultiplier = 1

Count = defaultdict(lambda: defaultdict(int))
Rules = defaultdict(dict)
Distribution = defaultdict(dict)
SourceToExtSource = defaultdict(set)
divergences = []
Verbose = True
StartingPoints = defaultdict(set)
Trajectory = []
MinSupport = 1

def Initialize():
    global Count
    global Rules
    global Distribution
    global SourceToExtSource
    global StartingPoints

    Count = defaultdict(lambda: defaultdict(int))
    Rules = defaultdict(dict)
    Distribution = defaultdict(dict)
    SourceToExtSource = defaultdict(set)
    StartingPoints = defaultdict(set)

def ExtractRules(T, MaxOrder, MS):
    Initialize()
    global Trajectory
    global MinSupport
    Trajectory = T
    MinSupport = MS
    BuildOrder(1, Trajectory, MinSupport)
    GenerateAllRules(MaxOrder, Trajectory, MinSupport)
    #DumpDivergences()
    return Rules


def BuildOrder(order, Trajectory, MinSupport):

    BuildObservations(Trajectory, order)
    BuildDistributions(MinSupport, order)
    #BuildSourceToExtSource(order)  # to speed up lookups
    #ObservationBuiltForOrder.add(order)


def BuildObservations(Trajectory, order):
    VPrint('building observations for order ' + str(order))
    LoopCounter = 0
    for Tindex in range(len(Trajectory)):
        LoopCounter += 1
        if LoopCounter % 10000 == 0:
            VPrint(LoopCounter)
        # remove metadata stored in the first element
        # this step can be extended to incorporate richer information
        trajectory = Trajectory[Tindex][1]

        for index in range(len(trajectory) - order):
            Source = tuple(trajectory[index:index+order])
            Target = trajectory[index+order]
            Count[Source][Target] += 1
            StartingPoints[Source].add((Tindex, index))

        # SubSequence = ExtractSubSequences(trajectory, order)
        # for sequence in SubSequence:
        #     Target = sequence[-1]
        #     Source = sequence[:-1]
        #     IncreaseCounter(Source, Target)


def BuildDistributions(MinSupport, order):
    VPrint('building distributions with MinSupport ' + str(MinSupport) +' and threshold multiplier ' + str(ThresholdMultiplier))
    for Source in Count:
        if len(Source) == order:
            for Target in Count[Source].keys():
                if Count[Source][Target] < MinSupport:
                    Count[Source][Target] = 0
            for Target in Count[Source]:
                if Count[Source][Target] > 0:
                    Distribution[Source][Target] = 1.0 * Count[Source][Target] / sum(Count[Source].values())


def GenerateAllRules(MaxOrder, Trajectory, MinSupport):
    VPrint('generating rules')
    progress = len(Distribution)
    VPrint(progress)
    LoopCounter = 0
    for Source in tuple(Distribution.keys()):
        AddToRules(Source)
        ExtendRule(Source, Source, 1, MaxOrder, Trajectory, MinSupport)
        LoopCounter += 1
        if LoopCounter % 10 == 0:
            VPrint('generating rules ' + str(LoopCounter) + ' ' + str(progress))


def ExtendRule(Valid, Curr, order, MaxOrder, Trajectory, MinSupport):
    if order >= MaxOrder:
        AddToRules(Valid)
    else:
        Distr = Distribution[Valid]
        # test if divergence has no chance exceeding the threshold when going for higher order
        #print(KLD(MaxDivergence(Distribution[Curr]), Distr), KLDThreshold(order+1, Curr))
        if KLD(MaxDivergence(Distribution[Curr]), Distr) < KLDThreshold(order+1, Curr):
            AddToRules(Valid)
        else:
            NewOrder = order + 1
            #if NewOrder not in ObservationBuiltForOrder:
            #    BuildOrder(NewOrder, Trajectory, MinSupport)
            #    VPrint(str(KLD(MaxDivergence(Distribution[Curr]), Distr)) + ' ' + str(KLDThreshold(order+1, Curr)))
            Extended = ExtendSourceFast(Curr)
            if len(Extended) == 0:
                AddToRules(Valid)
            else:
                for ExtSource in Extended:
                    ExtDistr = Distribution[ExtSource]  # Pseudocode in Algorithm 1 has a typo here
                    divergence = KLD(ExtDistr, Distr)
                    #divergences.append((NewOrder, ExtSource, Valid, divergence))
                    if divergence > KLDThreshold(NewOrder, ExtSource):
                        # higher-order dependencies exist for order NewOrder
                        # keep comparing probability distribution of higher orders with current order
                        ExtendRule(ExtSource, ExtSource, NewOrder, MaxOrder, Trajectory, MinSupport)
                    else:
                        # higher-order dependencies do not exist for current order
                        # keep comparing probability distribution of higher orders with known order
                        ExtendRule(Valid, ExtSource, NewOrder, MaxOrder, Trajectory, MinSupport)


def MaxDivergence(Distr):
    MaxValKey = sorted(Distr, key=Distr.__getitem__)
    d = {MaxValKey[0]: 1}
    return d


def AddToRules(Source):
    for order in range(1, len(Source)+1):
        s = Source[0:order]
        #print(s, Source)
        if not s in Distribution or len(Distribution[s]) == 0:
            ExtendSourceFast(s[1:])
        for t in Count[s]:
            if Count[s][t] > 0:
                Rules[s][t] = Count[s][t]
    # while len(Source) > 0:
    #     # To output frequencies instead of probabilities, change "Distribution" to "Count"
    #     # and filter out zero values
    #     if not Source in Distribution:
    #         ExtendSourceFast(Source[1:])
    #     Rules[Source] = Distribution[Source]
    #     PrevSource = Source[:-1]
    #     AddToRules(PrevSource)

###########################################
# Auxiliary functions
###########################################


def ExtractSubSequences(trajectory, order):
    SubSequence = []
    for starting in range(len(trajectory) - order + 1):
        SubSequence.append(tuple(trajectory[starting:starting + order]))
    return SubSequence


#def IncreaseCounter(Source, Target):
    #if not Source in Count:
    #    Count[Source] = Counter()
    #Count[Source][Target] += 1


def ExtendSourceSlow(Curr, NewOrder):
    Extended = []
    for CandidateSource in Distribution:
        if len(CandidateSource) == NewOrder and CandidateSource[-len(Curr):] == Curr:
            Extended.append(CandidateSource)
    return Extended


def ExtendSource(Curr, NewOrder):
    if Curr in SourceToExtSource:
        if NewOrder in SourceToExtSource[Curr]:
            return SourceToExtSource[Curr][NewOrder]
    return []


def ExtendSourceFast(Curr):
    if Curr in SourceToExtSource:
        return SourceToExtSource[Curr]
    else:
        ExtendObservation(Curr)
        if Curr in SourceToExtSource:
            return SourceToExtSource[Curr]
        else:
            return []


def ExtendObservation(Source):
    #print(Source)
    # if len(Source) == 1:
    #     # build SourceToExtSource
    #     C = defaultdict(lambda: defaultdict(int))
    #     for Tindex, index in StartingPoints[Source]:
    #         if index-1 >= 0 and index+1 < len(Trajectory[Tindex][1]):
    #             ExtSource = tuple(Trajectory[Tindex][1][index-1:index+1])
    #             Target = Trajectory[Tindex][1][index+1]
    #             C[ExtSource][Target] += 1
    #             StartingPoints[ExtSource].add((Tindex, index-1))
    #     if len(C) == 0:
    #         return
    #     for s in C:
    #         for t in C[s]:
    #             if C[s][t] < MinSupport:
    #                 C[s][t] = 0
    #             Count[s][t] += C[s][t]
    #         CsSupport = sum(C[s].values())
    #         for t in C[s]:
    #             if C[s][t] > 0:
    #                 Distribution[s][t] = 1.0 * C[s][t] / CsSupport
    #                 SourceToExtSource[s[1:]].add(s)
    # else:
    #print(Source)
    if len(Source) > 1:
        if (not Source[1:] in Count) or (len(Count[Source]) == 0):
            ExtendObservation(Source[1:])
    order = len(Source)
    C = defaultdict(lambda: defaultdict(int))
    #print(len(StartingPoints[Source]))
    # if len(StartingPoints[Source]) > 1000:
    #     with futures.ThreadPoolExecutor() as executor:
    #         Cs = executor.map(SubExtendObservation, [(x, order) for x in StartingPoints[Source]], chunksize=100)
    #         for c in Cs:
    #             for s in c:
    #                 for t in c[s]:
    #                     C[s][t] += c[s][t]
    # else:
    for Tindex, index in StartingPoints[Source]:
        if index - 1 >= 0 and index + order < len(Trajectory[Tindex][1]):
            ExtSource = tuple(Trajectory[Tindex][1][index - 1:index + order])
            Target = Trajectory[Tindex][1][index + order]
            C[ExtSource][Target] += 1
            StartingPoints[ExtSource].add((Tindex, index - 1))

    if len(C) == 0:
        return
    for s in C:
        for t in C[s]:
            if C[s][t] < MinSupport:
                C[s][t] = 0
            Count[s][t] += C[s][t]
        CsSupport = sum(C[s].values())
        for t in C[s]:
            if C[s][t] > 0:
                Distribution[s][t] = 1.0 * C[s][t] / CsSupport
                SourceToExtSource[s[1:]].add(s)


def SubExtendObservation(param):
    global Trajectory
    C = defaultdict(lambda: defaultdict(int))
    p, order = param
    Tindex, index = p
    if index - 1 >= 0 and index + order < len(Trajectory[Tindex][1]):
        ExtSource = tuple(Trajectory[Tindex][1][index - 1:index + order])
        Target = Trajectory[Tindex][1][index + order]
        C[ExtSource][Target] += 1
        StartingPoints[ExtSource].add((Tindex, index - 1))
    #print(C)
    return C


# creating a cache for fast lookup
def BuildSourceToExtSource(order):
    VPrint('Building cache')
    for source in Distribution:
        if len(source) == order:
            if len(source) > 1:
                NewOrder = len(source)
                for starting in range(1, len(source)):
                    curr = source[starting:]
                    if not curr in SourceToExtSource:
                        SourceToExtSource[curr] = {}
                    if not NewOrder in SourceToExtSource[curr]:
                        SourceToExtSource[curr][NewOrder] = set()
                    SourceToExtSource[curr][NewOrder].add(source)


def VPrint(string):
    if Verbose:
        print(string)


def KLD(a, b):
    divergence = 0
    for target in a:
        divergence += GetProbability(a, target) * math.log((GetProbability(a, target)/GetProbability(b, target)), 2)
    return divergence


def KLDThreshold(NewOrder, ExtSource):
    return ThresholdMultiplier * NewOrder / math.log(1 + sum(Count[ExtSource].values()), 2) # typo in Pseudocode in Algorithm 1


def GetProbability(d, key):
    if key not in d:
        return 0
    else:
        return d[key]


def DumpDivergences():
    with open('divergences.csv', 'w') as f:
        for pair in divergences:
            f.write(';'.join(map(str, pair)) + '\n')
