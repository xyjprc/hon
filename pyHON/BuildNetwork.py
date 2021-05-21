### This file: line-by-line translation from Algorithm 2
### in the paper "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Jan 2017

### Technical questions? Please contact i[at]jianxu[dot]net
### Demo of HON: please visit http://www.HigherOrderNetwork.com
### Latest code: please visit https://github.com/xyjprc/hon

### Call BuildNetwork()
### Input: Higher-order dependency rules
### Output: HON network
### See details in README


from collections import defaultdict, Counter

Graph = defaultdict(dict)
Verbose = True

def Initialize():
    Graph = defaultdict(dict)

def longestSuffix(s, rules_keys):
    ## returns the longest suffix of tuple 's'
    ## that exist in list of tuple rules_keys
    ## if s in rules_keys then returns s
    ss = s
    while len(ss)>1:
        if ss in rules_keys:
            return ss
        else:
            ss = ss[1:]
    return ss

def BuildNetwork(Rules):
    VPrint('Building network')
    Initialize()
    for s in Rules.keys():
        for t in Rules[s]:
            ## adding link s -> s*t where 
            ## and s* is the longest suffix of s 
            ## such that s*t is an existing rule
            nt = longestSuffix(s+(t,), Rules.keys())
            Graph[s][nt] = Rules[s][t]
    return Graph

###########################################
# Auxiliary functions
###########################################

def VPrint(string):
    if Verbose:
        print(string)
