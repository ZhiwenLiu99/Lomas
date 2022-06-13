if [ ! -d "../simulation_res/hpcc_EDU2" ];then
mkdir ../simulation_res/hpcc_EDU2
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=hp --trace=EDU2ADVTraffic --bw=100 --topo=fattree --hpai=50 --dir=hpcc_EDU2"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >hpcc_EDU2.log &