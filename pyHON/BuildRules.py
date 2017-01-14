### This file: line-by-line translation from Algorithm 1
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Jan 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/xyjprc/hon

### Call ExtractRules()
### Input: Trajectory
### Output: Higher-order dependency rules
### See details in README

from collections import defaultdict, Counter
import math

Count = {}
Rules = defaultdict(dict)
Distribution = defaultdict(dict)
SourceToExtSource = {}
Verbose = True

def Initialize():
    Count = {}
    Rules = defaultdict(dict)
    Distribution = defaultdict(dict)
    SourceToExtSource = {}


def ExtractRules(Trajectory, MaxOrder, MinSupport):
    Initialize()
    BuildObservations(Trajectory, MaxOrder)
    BuildDistributions(MinSupport)
    GenerateAllRules(MaxOrder)
    return Rules

def BuildObservations(Trajectory, MaxOrder):
    VPrint('building observations')
    LoopCounter = 0
    for record in Trajectory:
        LoopCounter += 1
        if LoopCounter % 1000 == 0:
            VPrint(LoopCounter)
        ## remove metadata stored in the first element
        ## this step can be extended to incorporate richer information
        trajectory = record[1]
        for order in range(2, MaxOrder+2):
            SubSequence = ExtractSubSequences(trajectory, order)
            for sequence in SubSequence:
                Target = sequence[-1]
                Source = sequence[:-1]
                IncreaseCounter(Source, Target)

def BuildDistributions(MinSupport):
    VPrint('building distributions')
    for Source in Count:
        for Target in Count[Source].keys():
            if Count[Source][Target] < MinSupport:
                Count[Source][Target] = 0
        for Target in Count[Source]:
            if Count[Source][Target] > 0:
                Distribution[Source][Target] = Count[Source][Target] / sum(Count[Source].values())

def GenerateAllRules(MaxOrder):
    VPrint('building cache')
    BuildSourceToExtSource() # to speed up lookups
    VPrint('generating rules')
    VPrint(len([x for x in Distribution if len(x) == 1]))
    LoopCounter = 0
    for Source in Distribution:
        if len(Source) == 1:
            AddToRules(Source)
            ExtendRule(Source, Source, 1, MaxOrder)
            LoopCounter += 1
            if LoopCounter % 100 == 0:
                VPrint(LoopCounter)

def ExtendRule(Valid, Curr, order, MaxOrder):
    if order >= MaxOrder:
        AddToRules(Valid)
    else:
        Distr = Distribution[Valid]
        NewOrder = order + 1
        Extended = ExtendSource(Curr, NewOrder)
        if len(Extended) == 0:
            AddToRules(Valid)
        else:
            for ExtSource in Extended:
                ExtDistr = Distribution[ExtSource] # Pseudocode in Algorithm 1 has a typo here
                if KLD(ExtDistr, Distr) > KLDThreshold(NewOrder, ExtSource):
                    # higher-order dependencies exist for order NewOrder
                    # keep comparing probability distribution of higher orders with current order
                    ExtendRule(ExtSource, ExtSource, NewOrder, MaxOrder)
                else:
                    # higher-order dependencies do not exist for current order
                    # keep comparing probability distribution of higher orders with known order
                    ExtendRule(Valid, ExtSource, NewOrder, MaxOrder)

def AddToRules(Source):
    if len(Source) > 0:
        ## To output frequencies instead of probabilities, change "Distribution" to "Count"
        ## and filter out zero values
        Rules[Source] = Distribution[Source]
        PrevSource = Source[:-1]
        AddToRules(PrevSource)

###########################################
# Auxiliary functions
###########################################

def ExtractSubSequences(trajectory, order):
    SubSequence = []
    for starting in range(len(trajectory) - order + 1):
        SubSequence.append(tuple(trajectory[starting:starting + order]))
    return SubSequence

def IncreaseCounter(Source, Target):
    if not Source in Count:
        Count[Source] = Counter()
    Count[Source][Target] += 1

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

## creating a cache for fast lookup
def BuildSourceToExtSource():
    for source in Distribution:
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
    return NewOrder / math.log(1 + sum(Count[ExtSource].values()), 2) # typo in Pseudocode in Algorithm 1

def GetProbability(d, key):
    if not key in d:
        return 0
    else:
        return d[key]