### This package: Python implementation of the higher-order network (HON) construction algorithm.
### Paper: "Representing higher-order dependencies in networks"
### Code written by Jian Xu, Jan 2017
### Technical questions? Please contact i[at]jianxu[dot]net

### See details in README


import BuildRules
import BuildNetwork


## Initialize algorithm parameters
MaxOrder = 5
MinSupport = 10

## Initialize user parameters
InputFileName = '../../data/traces-lloyds.csv'
OutputRulesFile = '../../data/rules-lloyds.csv'
OutputNetworkFile = '../../data/network-lloyds.csv'

LastStepsHoldOutForTesting = 3
MinimumLengthForTraining = 5
InputFileDeliminator = ' '
Verbose = True


###########################################
# Functions
###########################################

def ReadSequentialData(InputFileName):
    if Verbose:
        print('Reading raw sequential data')
    RawTrajectories = []
    with open(InputFileName) as f:
        LoopCounter = 0
        for line in f:
            fields = line.strip().split(InputFileDeliminator)
            ## In the context of global shipping, a ship sails among many ports
            ## and generate trajectories.
            ## Every line of record in the input file is in the format of:
            ## [Ship1] [Port1] [Port2] [Port3]...
            ship = fields[0]
            movements = fields[1:]

            LoopCounter += 1
            if LoopCounter % 10000 == 0:
                VPrint(LoopCounter)

            ## Other preprocessing or metadata processing can be added here

            ## Test for movement length
            MinMovementLength = MinimumLengthForTraining + LastStepsHoldOutForTesting
            if len(movements) < MinMovementLength:
                continue

            RawTrajectories.append([ship, movements])


    return RawTrajectories


def BuildTrainingAndTesting(RawTrajectories):
    VPrint('Building training and testing')
    Training = []
    Testing = []
    for trajectory in RawTrajectories:
        ship, movement = trajectory
        Training.append([ship, movement[:-LastStepsHoldOutForTesting]])
        Testing.append([ship, movement[-LastStepsHoldOutForTesting]])
    return Training, Testing

def DumpRules(Rules, OutputRulesFile):
    VPrint('Dumping rules to file')
    with open(OutputRulesFile, 'w') as f:
        for Source in Rules:
            for Target in Rules[Source]:
                f.write(' '.join([' '.join([str(x) for x in Source]), '=>', Target, str(Rules[Source][Target])]) + '\n')

def DumpNetwork(Network, OutputNetworkFile):
    VPrint('Dumping network to file')
    with open(OutputNetworkFile, 'w') as f:
        for source in Network:
            for target in Network[source]:
                f.write(','.join([SequenceToNode(source), SequenceToNode(target), str(Network[source][target])]) + '\n')

def SequenceToNode(seq):
    curr = seq[-1]
    node = curr + '|'
    seq = seq[:-1]
    while len(seq) > 0:
        curr = seq[-1]
        node = node + curr + '.'
        seq = seq[:-1]
    if node[-1] == '.':
        return node[:-1]
    else:
        return node

def VPrint(string):
    if Verbose:
        print(string)
###########################################
# Main function
###########################################

if __name__ == "__main__":
    RawTrajectories = ReadSequentialData(InputFileName)
    TrainingTrajectory, TestingTrajectory = BuildTrainingAndTesting(RawTrajectories)
    VPrint(len(TrainingTrajectory))
    Rules = BuildRules.ExtractRules(TrainingTrajectory, MaxOrder, MinSupport)
    DumpRules(Rules, OutputRulesFile)
    Network = BuildNetwork.BuildNetwork(Rules)
    DumpNetwork(Network, OutputNetworkFile)