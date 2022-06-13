if [ ! -d "../simulation_res/timely_all2all" ];then
mkdir ../simulation_res/timely_all2all
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=timely --trace=all2allTraffic --bw=100 --topo=fattree --hpai=50 --dir=timely_all2all"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >timely_all2all.log &