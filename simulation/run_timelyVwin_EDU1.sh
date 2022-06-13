if [ ! -d "../simulation_res/timelyVwin_EDU1" ];then
mkdir ../simulation_res/timelyVwin_EDU1
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=timely_vwin --trace=EDU1ADVTraffic --bw=100 --topo=fattree --hpai=50 --dir=timelyVwin_EDU1"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >timelyVwin_EDU1.log &