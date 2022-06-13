if [ ! -d "../simulation_res/timely_EDU1" ];then
mkdir ../simulation_res/timely_EDU1
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=timely --trace=EDU1ADVTraffic --bw=100 --topo=fattree --hpai=50 --dir=timely_EDU1"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >timely_EDU1.log &