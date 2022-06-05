from optparse import Option
import sys
from optparse import OptionParser

cur = 0
K = 10 # num host = 250
Bandwidth = 100
cores = []
pods = []
servers = []
links = []

def add_link(u, v, w):
    if u > v:
        u, v = v, u
    links.append((u, v, w,))

def add_core_aggregate(u, v):
    CORE_AGG = Bandwidth
    add_link(u, v, CORE_AGG)

def add_edge(u, v):
    EDGE = Bandwidth
    add_link(u, v, EDGE)

def add_in_pods(u, v):
    INP = Bandwidth
    add_link(u, v, INP)

def gen():
    global cur
    cnum = (K // 2) ** 2
    hnum = K ** 3 // 4
    for i in range(hnum):
        servers.append(cur)
        cur += 1
    for i in range(cnum):
        cores.append(cur)
        cur += 1
    ctr = 0
    for i in range(K):
        pod = []
        for j in range(K):
            pod.append(cur)
            cur += 1

        #pod[0], [1] are edges
        #pod[2], [3] are to cores
        add_in_pods(pod[0], pod[2])
        add_in_pods(pod[0], pod[3])
        add_in_pods(pod[1], pod[2])
        add_in_pods(pod[1], pod[2])
        for j in range(cnum):
            add_core_aggregate(pod[j % (K // 2)], cores[j])
        for j in range(K * K // 4):
            add_edge(pod[j // K], servers[ctr])
            ctr += 1
        pods.append(pod)    
    print "hostnum: ", hnum         
    assert(ctr == hnum)

def print_topo(file_name, delay, error_rate):
    with open(file_name, "w+") as f:
        f.write("{} {} {}\n".format(cur, cur - len(servers), len(links)))
        for i in cores:
            f.write(str(i) + ' ')
        for i in pods:
            for j in i:
                f.write(str(j) + ' ')
        f.write('\n')
        for u, v, w in links:
            f.write("{} {} {}Gbps {}ms {}\n".format(u, v, w, delay, error_rate))


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-k','--k', dest='k_ary', help='k-ary fat-tree', default=10)
    parser.add_option('-b', '--bandwidth', dest='bandwidth', help='the bandwidth of link (G)', default=100)
    parser.add_option('-d', '--delay', dest='delay', help='the propagation delay of each link (ms)', default=0.01)
    parser.add_option('-e', '--error', dest='error', help='the error rate of each link', default=0)
    parser.add_option('-o', '--output', dest='output', help='path of output file', default="topology.txt")
    options, args = parser.parse_args()

    K = int(options.k_ary)
    Bandwidth = int(options.bandwidth)

    gen()
    print_topo(options.output, float(options.delay), float(options.error))
