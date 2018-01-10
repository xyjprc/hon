#import concurrent.futures
import glob
import main

InputTrajectoryFiles = glob.glob('../data/GSN/*')


#args = ((fn, '\\'.join(fn.split('\\')[:-1]) + 'network-synthetic-1M' + fn.split('\\')[-1]) for fn in InputTrajectoryFiles)

#with concurrent.futures.ProcessPoolExecutor() as executor:
#    executor.map(main.BuildHON, InputTrajectoryFiles)

for fn in InputTrajectoryFiles:
    print(fn)
    main.BuildHON(fn, '\\'.join(fn.split('/')[:-1]) + '/network-GSN/' + fn.split('\\')[-1])
