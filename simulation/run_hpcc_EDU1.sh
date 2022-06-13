if [ ! -d "../simulation_res/hpcc_EDU1" ];then
mkdir ../simulation_res/hpcc_EDU1
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=hp --trace=EDU1ADVTraffic --bw=100 --topo=fattree --hpai=50 --dir=hpcc_EDU1"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >hpcc_EDU1.log &