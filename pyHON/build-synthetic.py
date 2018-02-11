import random
import concurrent.futures


def NextStep(port):
    ##random.seed()
    #up = (port - 10) % 100
    down = (port + 10) % 100
    #left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    return random.choice([down, right])

def BiasedNextStep(port):
    #random.seed()
    #up = (port - 10) % 100
    down = (port + 10) % 100
    #left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    rnd = random.random()
    if rnd < .9:
        return right
    else:
        return down

def AltBiasedNextStep(port):
    #random.seed()
    # up = (port - 10) % 100
    down = (port + 10) % 100
    # left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    rnd = random.random()
    if rnd < .1:
        return right
    else:
        return down


def MixedBiasedNextStep(port):
    #random.seed()
    # up = (port - 10) % 100
    down = (port + 10) % 100
    # left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    rnd = random.random()
    if rnd < 110/300:
        return right
    else:
        return down

def AltMixedBiasedNextStep(port):
    #random.seed()
    # up = (port - 10) % 100
    down = (port + 10) % 100
    # left = (port - 1) % 10 + 10 * int(port / 10)
    right = (port + 1) % 10 + 10 * int(port / 10)
    rnd = random.random()
    if rnd < 190/300:
        return right
    else:
        return down

def WriteTrajectories(trajectories, iteration, NetType):
    StrIteration = str(iteration)
    while len(StrIteration) < 4:
        StrIteration = '0' + StrIteration
    print(StrIteration, NetType)
    with open(OutputFolder + StrIteration + '_' + NetType + '.csv', 'w') as f:
        vid = 1
        for trajectory in trajectories:
            f.write(str(vid) + ' ' + ' '.join(map(str, trajectory)) + '\n')
            vid += 1

# normal
def SynthesizeNormal(NetworkPrefixCounter):
    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            ###random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                port = NextStep(trajectory[-1])
            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'normal')


# add first order

def SynthesizeAddFirstOrder(NetworkPrefixCounter):
    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                prev = trajectory[-1]
                if prev in [0, 3, 6]:
                    port = BiasedNextStep(prev)
                else:
                    port = NextStep(prev)
            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddFirstOrder')


# modify first order

def SynthesizeModifyFirstOrder(NetworkPrefixCounter):
    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                prev = trajectory[-1]
                if prev in [0, 3, 6]:
                    port = AltBiasedNextStep(prev)
                else:
                    port = NextStep(prev)
            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'ModifyFirstOrder')


# add second order

def SynthesizeAddSecondOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    prev = trajectory[-1]
                    pprev = trajectory[-2]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        if (pprev, prev) in [(27, 28)]:
                            port = BiasedNextStep(prev)
                        else:
                            port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddSecondOrder')


# Add sophisticated second order

def SynthesizeAddSophisticatedSecondOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    prev = trajectory[-1]
                    pprev = trajectory[-2]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        if (pprev, prev) in [(27, 28)]:
                            port = BiasedNextStep(prev)
                        elif (pprev, prev) in [(30, 31), (34, 35)]:
                            port = BiasedNextStep(prev)
                        elif (pprev, prev) in [(21, 31), (25, 35)]:
                            port = AltBiasedNextStep(prev)
                        else:
                            port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddSophisticatedSecondOrder')


# modify second order
def SynthesizeModifySecondOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    prev = trajectory[-1]
                    pprev = trajectory[-2]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        if (pprev, prev) in [(27, 28)]:
                            port = BiasedNextStep(prev)
                        elif (pprev, prev) in [(30, 31), (34, 35)]:
                            port = AltBiasedNextStep(prev)
                        elif (pprev, prev) in [(21, 31), (25, 35)]:
                            port = BiasedNextStep(prev)
                        else:
                            port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'ModifySophisticatedSecondOrder')


# add third order
def SynthesizeAddThirdOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)
                    else:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        ppprev = trajectory[-3]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(61, 71, 81)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddThirdOrder')


# add sophisticated third order
def SynthesizeAddSophisticatedThirdOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)
                    else:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        ppprev = trajectory[-3]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(61, 71, 81)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(73, 74, 84), (76, 77, 87)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(64, 74, 84), (67, 77, 87)]:
                                port = AltBiasedNextStep(prev)
                            else:
                                port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddSophisticatedThirdOrder')


# modify third order
def SynthesizeModifyThirdOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)
                    else:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        ppprev = trajectory[-3]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(61, 71, 81)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(73, 74, 84), (76, 77, 87)]:
                                port = AltBiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(64, 74, 84), (67, 77, 87)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'ModifyThirdOrder')


# add mixed first and third order
def SynthesizeAddMixedOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)
                    else:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        ppprev = trajectory[-3]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(61, 71, 81)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(73, 74, 84), (76, 77, 87)]:
                                port = AltBiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(64, 74, 84), (67, 77, 87)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(39, 49, 59)]:
                                port = BiasedNextStep(prev)
                            elif prev == 59:
                                port = MixedBiasedNextStep(prev)
                            else:
                                port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'AddMixedOrder')


# modify mixed first and third order
def SynthesizeModifyMixedOrder(NetworkPrefixCounter):

    trajectories = []
    for vessel in range(vessels):
        trajectory = []
        for step in range(steps):
            #random.seed()
            if len(trajectory) == 0:
                port = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]
                    if prev in [0, 3, 6]:
                        port = AltBiasedNextStep(prev)
                    else:
                        port = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            else:
                                port = NextStep(prev)
                    else:
                        prev = trajectory[-1]
                        pprev = trajectory[-2]
                        ppprev = trajectory[-3]
                        if prev in [0, 3, 6]:
                            port = AltBiasedNextStep(prev)
                        else:
                            if (pprev, prev) in [(27, 28)]:
                                port = BiasedNextStep(prev)
                            elif (pprev, prev) in [(30, 31), (34, 35)]:
                                port = AltBiasedNextStep(prev)
                            elif (pprev, prev) in [(21, 31), (25, 35)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(61, 71, 81)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(73, 74, 84), (76, 77, 87)]:
                                port = AltBiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(64, 74, 84), (67, 77, 87)]:
                                port = BiasedNextStep(prev)
                            elif (ppprev, pprev, prev) in [(39, 49, 59)]:
                                port = AltBiasedNextStep(prev)
                            elif prev == 59:
                                port = AltMixedBiasedNextStep(prev)
                            else:
                                port = NextStep(prev)

            trajectory.append(port)
        trajectories.append(trajectory)
    WriteTrajectories(trajectories, NetworkPrefixCounter, 'ModifyMixedOrder')


################ main

NetworkPrefixCounter = 0
OutputFolder = '../data/synthetic/'
iterations = 10
vessels = 100000
steps = 100

if __name__ == '__main__':

    # every node has 40000*100/100=40000 movements on a 10x10 grid
    random.seed()


    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeNormal, range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddFirstOrder, range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeModifyFirstOrder, range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddSecondOrder, range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddSophisticatedSecondOrder, range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeModifySecondOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddThirdOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddSophisticatedThirdOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeModifyThirdOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeAddMixedOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(SynthesizeModifyMixedOrder,
                     range(NetworkPrefixCounter, NetworkPrefixCounter + iterations))

    NetworkPrefixCounter += iterations

