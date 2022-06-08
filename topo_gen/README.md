# Topology Generator

This folder includes the scripts for generating topologies.

## Usage

`python topo_gen_fattree.py -h` for help.

Example:
`python topo_gen_fattree.py -k 10 -b 100 -o ./output/fattree.txt` generates a 10-ary fat-tree, with 250 hosts. And the bandwidth is 100Gbps.

The generate topology can be directly used by the simulation.

## Topology format

The first line is stats of this topology: `<number of nodes> <number of switches> <number of links>`.

The second line is the ID of switches: `<switch id1> ... <switch idn>`.

Each line after that is a link: `<src node> <dst node> <bandwidth> <propagation delay (ms)> <error rate>`.

**P.S.** server-IDs and switch-IDs count from 0 to N-1 (N is the total number of nodes), and the switch-IDs and are positioned after server-IDs.

## Schemes

Currently, we provide 2 kinds of topologies:

* star-like: N-1 servers connected to 1 switch
* fat-tree: [A Scalable, Commodity Data Center Network Architecture](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)


## Environment

python >= 3.6
