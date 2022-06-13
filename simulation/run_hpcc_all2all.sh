if [ ! -d "../simulation_res/hpcc_all2all" ];then
mkdir ../simulation_res/hpcc_all2all
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=hp --trace=all2allTraffic --bw=100 --topo=fattree --hpai=50 --dir=hpcc_all2all"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >hpcc_all2all.log &