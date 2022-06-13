# NS-3 simulation result

This folder contains NS-3 simulation result for HPCC, Timely(-win), DCQCN(-win) and DCTCP

### FCT Format

Each line is a flow fct info: `<src host> <dst host> <src port (const 10000)> <dst port (const 100)> <flow size (bytes)> <start time (ns)> <fct (ns)> <standalone fct (ns)>`

### FCT analysis

`fct_analysis.py` is used to analyze fct (CC simulation output). It reads multiple fct files (simulation's output), and prints data that can produce figures like Figure 11 (a) and (c) in [HPCC paper](https://liyuliang001.github.io/publications/hpcc.pdf).

Usage: please check `python fct_analysis.py -h` and read line 20-26 in `fct_analysis.py`

### Demo

![fct_analysis_demo](https://github.com/ZhiwenLiu99/Lomas/blob/master/img/fct_analysis.png)

### Detected problems

**[Simulation]** When using EDU1 and EDU2 traces, Timely and DCQCN will never finish because of PFC-deadlock (a possible reason). Timely-win and DCQCN-win however work well. (by Banruo Liu) (Fixed in `traffic_gen_EDUx_adv.py`)

### Environment

python >= 3.6
