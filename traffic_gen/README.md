# Traffic Generator

This folder includes the scripts for generating traffic.

## Usage

#### For all2all & incast

`python traffic_gen_xxx.py -h` for help.

Example:
`python traffic_gen.py -c WebSearch_distribution.txt -n 320 -l 0.3 -b 100G -t 0.1` generates traffic according to the web search flow size distribution, for 320 hosts, at 30% network load with 100Gbps host bandwidth for 0.1 seconds.

We provide 4 flow-size distributions to generate all2all & incast trace. `WebSearch_distribution.txt` and `FbHdp_distribution.txt` are the ones used in the HPCC paper. `AliStorage2019.txt` are collected from Alibaba's production distributed storage system in 2019. `GoogleRPC2008.txt` are Google's RPC size distribution before 2008.

#### For EDU1_adv & EDU2_adv

We use trained model by *Lomas (APNet`22)* to generate two real world datacenter traces ([EDU1 and EDU2](https://pages.cs.wisc.edu/~tbenson/IMC10_Data.html)).

The suffix '_avd'  means we add some advanced features (e.g. adjusting interarrival-time to mimic different level of load/demand, and different number of servers).

 `python traffic_gen_EDUx_adv.py -h` for help. 

When a larger n is chosen, we use the `nearest neighbor upscaling method`  (just like upscale an image, we upscale the traffic matrix) to spread the pixels (servers) out and fill in the holes by copying the flow patterns from the closest pixels.

> For EDU1, the number of servers should be larger than 203 (which is the ground truth in training data). And for EDU2, the number of servers should be larger than 233.

#### For EDU1 & EDU2 (Deprecated)

We use trained model by *Lomas (APNet`22)* to generate two real world datacenter traces ([EDU1 and EDU2](https://pages.cs.wisc.edu/~tbenson/IMC10_Data.html)).

`python traffic_gen_EDUx.py -h` for help.

## Traffic format

The first line is the number of flows.

Each line after that is a flow: `<source host> <dest host> <priority (const 3)> <dest port number (const 100)> <flow size (bytes)> <start time (seconds)>`

## Environment

python >= 3.6
