comm_arg="-n 203 -c ./stats_EDU1/cdf_size.txt -b 100G -t 0.01 -o ./output/all2allTraffic.txt"
exe="python traffic_gen_all2all.py"

${exe} ${comm_arg}