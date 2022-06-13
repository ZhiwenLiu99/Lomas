import os
import subprocess
import argparse
import pandas as pd
import numpy as np

def get_pctl(a, p):
	i = int(len(a) * p)
	return a[i]

def q50(x):
    return x.quantile(0.5)

def q95(x):
    return x.quantile(0.95)

def q99(x):
    return x.quantile(0.99)

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-p', dest='postfix', action='store', default='all2all', help="Specify the postfix of the fct file.")
	parser.add_argument('-s', dest='step', action='store', default='5')
	parser.add_argument('-t', dest='type', action='store', type=int, default=0, help="0: normal, 1: incast, 2: all")
	parser.add_argument('-T', dest='time_limit', action='store', type=int, default=3e12, help="only consider flows that finish before T")
	parser.add_argument('-b', dest='bw', action='store', type=int, default=25, help="bandwidth of edge link (Gbps)")
	args = parser.parse_args()

	type = args.type
	time_limit = args.time_limit

	# Get all the cc (together with parameters) that you want to compare under a specific traffic pattern (with the same postfix).
	CCs = []
	for f in os.listdir('./'):
		cc = os.path.join('./', f)
		if os.path.isdir(cc) and f.endswith(args.postfix):
			CCs.append(cc)

	step = int(args.step)
	res = [[i/100.] for i in range(0, 100, step)]
	xbound = [0, 256, 512, 1024, 4096, 32768, 131072, 1048576, 10485760, 52428800, 104857600]
	xlable = ['0', '256', '512', '1K', '4K', '32K', '128K', '1M', '10M', '50M', '100M']

	for cc in CCs:
		#file = "%s_%s.txt"%(args.prefix, cc)
		# find fct output for each simulation
		for file in os.listdir(cc):
			if file.startswith('fct_'):
				break
		file = os.path.join(cc, file)
		if type == 0:
			''' $6: start time, $7: fct, $8: standalone fct, $5: flow size '''
			cmd = "cat %s"%(file)+" | awk '{if ($4==100 && $6+$7<"+"%d"%time_limit+") {slow=$7/$8;print slow<1?1:slow, $5}}' | sort -n -k 2"
			# print cmd
			output = subprocess.check_output(cmd, shell=True)
		elif type == 1:
			''' $6: start time, $7: fct, $8: standalone fct, $5: flow size '''
			cmd = "cat %s"%(file)+" | awk '{if ($4==200 && $6+$7<"+"%d"%time_limit+") {slow=$7/$8;print slow<1?1:slow, $5}}' | sort -n -k 2"
			#print cmd
			output = subprocess.check_output(cmd, shell=True)
		else:
			''' $6: start time, $7: fct, $8: standalone fct, $5: flow size '''
			cmd = "cat %s"%(file)+" | awk '{$6+$7<"+"%d"%time_limit+") {slow=$7/$8;print slow<1?1:slow, $5}}' | sort -n -k 2"
			#print cmd
			output = subprocess.check_output(cmd, shell=True)

		# up to here, `output` should be a string of multiple lines, each line is: fct, size
		a = output.split('\n')[:-2]
		n = len(a)
		for i in range(0,100,step):
			l = i * n / 100
			r = (i+step) * n / 100
			d = map(lambda x: [float(x.split()[0]), int(x.split()[1])], a[l:r])
			fct=sorted(map(lambda x: x[0], d))
			res[i/step].append(d[-1][1]) # flow size
			#res[i/step].append(sum(fct) / len(fct)) # avg fct
			res[i/step].append(get_pctl(fct, 0.5)) # mid fct
			res[i/step].append(get_pctl(fct, 0.95)) # 95-pct fct
			res[i/step].append(get_pctl(fct, 0.99)) # 99-pct fct
		
		# a = output.split('\n')[:-2]
		# a = [[float(i.split(' ')[0]), int(i.split(' ')[1])] for i in a]
		# df = pd.DataFrame(a, columns=['fct', 'size'])
		# df['tag'] = pd.cut(df['size'], bins=xbound, labels=xlable[1:])
		# df = df.groupby('tag')['fct'].agg([q50, q95, q99])

	for item in res:
		line = "%.3f %d"%(item[0], item[1])
		i = 1
		for cc in CCs:
			line += "\t%.3f %.3f %.3f"%(item[i+1], item[i+2], item[i+3])
			i += 4
		print(line)

	import pdb
	pdb.set_trace()