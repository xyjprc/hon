# Synthesizes trajectories of vessels going certain steps on a 10x10 mesh
# 10,000,000 movements will be generated by default.
# Normally a vessel will go either up/down/left/right with the same probability
# (vessel movements are generated almost randomly with the following exceptions)

# But we add a few higher order rules:
# 2nd order rule: if vessel goes right from X0 to node X1 (X means a number 0-9)
# then the next step will go right with probability 70%, go down 30% (BiasedNextStep)
# 3rd order rule: if vessel goes right to node X7 then X8
# then the next step will go right with probability 70%, go down 30%
# 4th order rule: if vessel goes down from 1X to 2X to 3X to 4X
# then the next step will go right with probability 70%, go down 30%
# There are ten 2nd order rules, ten 3rd order rules, ten 4th order rules, no other rules

# Use HON with a default setting of MaxOrder = 5, MinSupport = 5, tolerance = 0.1
# It should be able to detect all 30 of these rules of various orders
# And will not detect "false" dependencies such as 5th order rules.
# The whole time to process these 10,000,000 movements should be under 30 seconds.


import random
from time import time

NumOfVessels = 100000
LengthOfTrace = 100

start = time()
def NextStep(port):
    random.seed()
    up = (port - 10) % 100
    down = (port + 10) % 100
    left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    return random.choice([up, down, left, right])


def OrderTwoNext(prev1, prev2):
    if IsLeft(prev2, prev1):
        if prev1 % 10 == 1:
            return BiasedNextStep(prev1)
    return NextStep(prev1)


def OrderThreeNext(prev1, prev2, prev3):
    if IsLeft(prev2, prev1):
        if IsLeft(prev3, prev2):
            if prev1 % 10 == 8:
                return BiasedNextStep(prev1)
        if prev1 % 10 == 1:
            return BiasedNextStep(prev1)
    return NextStep(prev1)


def OrderFourNext(prev1, prev2, prev3, prev4):
    if IsUp(prev4, prev3):
        if IsUp(prev3, prev2):
            if IsUp(prev2, prev1):
                if int(prev1 / 10) == 4:
                    return BiasedNextStep(prev1)
    if IsLeft(prev2, prev1):
        if IsLeft(prev3, prev2):
            if prev1 % 10 == 8:
                return BiasedNextStep(prev1)
        if prev1 % 10 == 1:
            return BiasedNextStep(prev1)
    return NextStep(prev1)




def IsLeft(pa, pb):
    if (pa + 1) % 10 + int(pa / 10) * 10 == pb:
        return True
    else:
        return False


def IsUp(pa, pb):
    if (pa + 10) % 100 == pb:
        return True
    else:
        return False



def BiasedNextStep(port):
    random.seed()
    down = (port + 10) % 100
    right = (port + 1) % 10 + 10 * int(port / 10)
    rnd = random.random()
    if rnd > .7:
        return right
    else:
        return down


traces = [None]*NumOfVessels

for vessel in range(NumOfVessels):
    if vessel % 100 == 0:
        print(vessel)
    trace = [None]*LengthOfTrace
    for step in range(LengthOfTrace):
        port = -1
        random.seed()
        # if len(trace) == 0:
        if step == 0:
            port = random.randint(0, 99)
        # if len(trace) == 1:
        elif step == 1:
            # port = NextStep(trace[-1])
            # step = 1  previous step - 1 = 0 ; trace[0]
            port = NextStep(trace[step-1])
        # if len(trace) == 2:
        elif step == 2:
            # port = OrderTwoNext(trace[-1], trace[-2])
            # step = 2 , index 1, 0
            port = OrderTwoNext(trace[step-1] , trace[step-2])
        # if len(trace) == 3:
        elif step == 3:
            # port = OrderThreeNext(trace[-1], trace[-2], trace[-3])
            # step = 3 index = 2,1,0
            port = OrderThreeNext(trace[step-1], trace[step-2], trace[step-3])
        # if len(trace) >= 4:
        elif step >= 4:
            # port = OrderFourNext(trace[-1], trace[-2], trace[-3], trace[-4])
            # step 4 : index 3, 2, 1, 0
            # step 5 : index 4, 3, 2, 1
            port = OrderFourNext(trace[step-1], trace[step-2], trace[step-3], trace[step-4])
        trace[step] = port
    traces[vessel] = trace

with open('traces-simulated-mesh-v100000-t100-mo4.csv', 'w') as f:
    # vin = 1
    # for trace in traces:
    #     f.write(str(vin) + ' ' + ' '.join([str(x) for x in trace]) + '\n')
    #     vin += 1
    for vin , trace in enumerate(traces):
        f.write(str(vin + 1) + ' ' + ' '.join([str(x) for x in trace]) + '\n')

end = time()
print("Total seconds : " , round(end - start , 2))