if [ ! -d "../simulation_res/timely_EDU2" ];then
mkdir ../simulation_res/timely_EDU2
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=timely --trace=EDU2ADVTraffic --bw=100 --topo=fattree --hpai=50 --dir=timely_EDU2"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >timely_EDU2.log &