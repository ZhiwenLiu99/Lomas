comm_arg = "-n 65 -c ./stats_all2all/WebSearch_distribution.txt -b 100G -t 0.1 -o ./output/centralTraffic.txt"
exe = "python traffic_gen_all2all.py"

${exe} ${comm_arg}