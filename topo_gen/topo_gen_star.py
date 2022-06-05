from random import random
import sys
import random
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-n','--nnode', dest='nnode', help='number of nodes', default=66)
    parser.add_option('-b', '--bandwidth', dest='bandwidth', help='the bandwidth of link (G)', default=100)
    parser.add_option('-d', '--delay', dest='delay', help='the propagation delay of each link (ms)', default=0.01)
    parser.add_option('-e', '--error', dest='error', help='the error rate of each link', default=0)
    parser.add_option('-o', '--output', dest='output', help='path of output file', default="topology.txt")
    options, args = parser.parse_args()

    N = int(options.nnode)
    Switch = N-1
    Bandwidth = int(options.bandwidth)
    Delay = float(options.delay)
    Error = float(options.error)
    link = []

    for i in range(0, N-1):
        link.append((i, Switch))
    with open(options.output, "w+") as f:
        f.write("{} {} {}\n".format(N, 1, len(link)))
        f.write(str(Switch) + '\n')
        for i in link:
            f.write("{} {} {}Gbps {}ms {}\n".format(i[0], i[1], Bandwidth, Delay, Error))
        