# Visualization

* Flow level traffic pattern (EDU1)

![perPair_final2](https://github.com/ZhiwenLiu99/Lomas/blob/master/img/perPair_final2.png)

* Flow level traffic pattern (all2all synthetic trace)

![perPair_final_all2all](https://github.com/ZhiwenLiu99/Lomas/blob/master/img/perPair_final_all2all.png)

# Analysis

This folder includes code and scripts for visualization and analysis.

## FCT analysis

`fct_analysis.py` is used to analyze fct (CC simulation output). It reads multiple fct files (simulation's output), and prints data that can produce figures like Figure 11 (a) and (c) in [HPCC paper](https://liyuliang001.github.io/publications/hpcc.pdf).

Usage: please check `python fct_analysis.py -h` and read line 20-26 in `fct_analysis.py`
