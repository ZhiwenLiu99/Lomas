if [ ! -d "../simulation_res/timelyVwin_all2all" ];then
mkdir ../simulation_res/timelyVwin_all2all
else
echo "already has simulation results" 
exit
fi

comm_arg="--cc=timely_vwin --trace=all2allTraffic --bw=100 --topo=fattree --hpai=50 --dir=timelyVwin_all2all"
exe='python -u ./run_modify.py'

nohup ${exe} ${comm_arg} 2>&1 >timelyVwin_all2all.log &