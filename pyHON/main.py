### Python implementation of the higher-order network (HON) construction algorithm.
### Paper: "Representing higher-order dependencies in networks"
### Code written by Jian Xu
### Technical questions? Please contact i[at]jianxu[dot]net

import BuildRules
from collections import defaultdict

## Initialize algorithm parameters
MaxOrder = 5
MinSupport = 10

## Initialize user parameters
InputFileName = '../../data/traces-lloyds.csv'
OutputRulesFile = '../../data/rules-lloyds.csv'
#InputFileName = '../../data/traces-test.csv'
#OutputRulesFile = '../../data/rules-test.csv'
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
                f.write(' '.join([' '.join([str(x) for x in Source]), '=>', Target, str(Rules[Source][Target]), '\n']))

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