import glob
from concurrent import futures
import os
import main
import helper


#def sub(i):
#    cmd = '/usr/bin/python /afs/crc.nd.edu/user/j/jxu5/hon_anomaly/pyHON/helper.py ' + str(i)
#    print(cmd)
#    os.sys(cmd)
if __name__ == '__main__':
    FNs = glob.glob('../data/NYC-week/*')
    #cmd = ['/usr/bin/python /afs/crc.nd.edu/user/j/jxu5/hon_anomaly/pyHON/helper.py ' + str(x) for x in FNs]


    #with futures.ProcessPoolExecutor() as executor:
    #    executor.map(helper.helper, FNs)


    for fn in FNs:
        helper.helper(fn)
