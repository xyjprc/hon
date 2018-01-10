#import concurrent.futures
import main
import sys

def helper(arg):
    fn = arg
    fnout = '/'.join(fn.split('/')[:2]) + '/network-nyc-week-freq/' + fn.split('/')[-1]
    print(fn, fnout)
    main.BuildHONfreq(fn, fnout)
