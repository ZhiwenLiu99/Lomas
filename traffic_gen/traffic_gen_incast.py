"""
incast traffic pattern (default using star-like topology)
"""

from email.policy import default
from random import random
import sys
import random
from optparse import OptionParser


def delta():
    return random.randint(1, 4) * (10 ** -7)

def getsize():
    return random.randint(1, 10) * (10 ** 6) 

def gen(n, victim, base_t, epoch):
    """
    n: number of server
    victim: incast to which server?
    base_t: time to start
    epoch: number of epoch
    """
    start = 0
    flow = []
    for j in range(epoch):
        for i in range(n):
            if i != victim:
                flow.append((i, victim, 3, 100, getsize(), base_t*1e-9 + start))
                start += delta()
    return flow


if __name__ == "__main__":
    base_t = 2e9  # start from 2s
    epoch = 5     # number of round

    parser = OptionParser()
    parser.add_option("-n", "--nhost", dest="nhost", help="number of host", default=65)
    parser.add_option("-o", "--output", dest="output", help="the output file", default="incastTraffic.txt")
    options, args = parser.parse_args()
    
    flow = gen(n=options.nhost, victim=0, base_t=base_t, epoch=epoch)
    
    with open(options.output, "w+") as f:
        f.write(str(len(flow)) + '\n')
        for i in flow:
            f.write("{} {} {} {} {} {:.9f}\n".format(i[0], i[1], i[2], i[3], i[4], i[5]))