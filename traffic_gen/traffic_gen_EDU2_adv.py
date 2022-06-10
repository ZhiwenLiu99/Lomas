# -*- coding: utf-8 -*

import sys
import os
import re
import random
import numpy as np
import pandas as pd
from optparse import OptionParser

from gensim import corpora
from gensim.models import LdaModel

def translate_bandwidth(b):
	if b == None:
		return None
	if type(b)!=str:
		return None
	if b[-1] == 'G':
		return float(b[:-1])*1e9
	if b[-1] == 'M':
		return float(b[:-1])*1e6
	if b[-1] == 'K':
		return float(b[:-1])*1e3
	return float(b)

def sample_time(cdf, tag):
    percent = list(cdf['percentile'].values)
    bounds = cdf['cdf'].values
    idx = percent.index(tag)
    x0 = percent[idx-1]
    y0 = bounds[idx-1]
    x1 = tag
    y1 = bounds[idx]
    x = np.random.uniform(low=x0, high=x1, size=None)
    return y0 + (y1-y0)/(x1-x0)*(x-x0)

def sample_size(cdf, tag):
    percent = list(cdf['percentile'].values)
    bounds = cdf['cdf'].values
    idx = percent.index(tag)
    x0 = percent[idx-1]
    y0 = bounds[idx-1]
    x1 = tag
    y1 = bounds[idx]
    x = np.random.uniform(low=x0, high=x1, size=None)
    return y0 + (y1-y0)/(x1-x0)*(x-x0)

def getAvg(cdf):
    '''
    x-axis: values (e.g. flow size)
    y-axis: percentile (0-100)
    '''
    s = 0
    last_x, last_y = cdf[0]
    for c in cdf[1:]:
        x, y = c
        s += (x + last_x)/2.0 * (y - last_y)
        last_x = x
        last_y = y
    return s/100

def get_mean_from_cdf(cdf):
    prob = cdf['percentile']
    x = cdf['cdf']
    r = 0
    t = [(x[i], prob[i]) for i in range(len(prob))]
    ret = getAvg(t)
    #print("avg interval =" + str(ret))
    return ret

def get_divider(length, threshold, divider, param):
    '''
    normalize flow inter to fit target load (which can be calculated from traffic_gen_all2all.py)
    '''
    if (length > threshold):
        return param * divider 
    else:
        return param * divider * (length / threshold) ** 2

if __name__ == "__main__":
    np.random.seed(2022)
    base_t = 2e9                   # start from 2s
    multiplier = 0.55              # hyperparameter, used to adj the interval-distribution to target interval
    large_interval_threshold = 3   # hyperparameter, boundary to distinguish abnormal large flow-interval

    parser = OptionParser()
    parser.add_option("-n", "--nhost", dest = "nhost", help = "number of hosts", default=233)
    parser.add_option("-l", "--load", dest = "load", help = "the percentage of the traffic load to the network capacity, by default 0.3", default = "0.3")
    parser.add_option("-b", "--bandwidth", dest = "bandwidth", help = "the bandwidth of host link (G/M/K), by default 10G", default = "10G")
    parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 1", default = "1")
    parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "tmp_traffic.txt")
    options,args = parser.parse_args()

    ###############  load cdf  ###############
    cdf_size = pd.read_csv("./stats_EDU2/cdf_size.csv", index_col=[0])
    cdf_interval = pd.read_csv("./stats_EDU2/cdf_interval.csv", index_col=[0])

    ###############  calculate params  ###############
    nhost = int(options.nhost)
    load = float(options.load)
    bandwidth = translate_bandwidth(options.bandwidth)
    avg_size = getAvg(cdf_size[['cdf', 'percentile']].values)
    target_interval = 1/(bandwidth*load/8./avg_size)*1e9
    real_avg_interval = getAvg(cdf_interval[['cdf', 'percentile']].values)*1e9
    divider = real_avg_interval / target_interval
    
    time_limit = float(options.time)*1e9 # translates to ns

    ###############  load model  ###############
    dictionary = corpora.Dictionary.load("./model_EDU2/qzone.dict")      
    doc_topics = pd.read_csv("./model_EDU2/res_document_topics.csv", index_col=[0]).values  # document-topic matrix
    doc_topics = np.divide(doc_topics, np.sum(doc_topics, axis=1).reshape(-1,1))       # normalize each row to sum to 1
    model = LdaModel.load("./model_EDU2/qzone.model", mmap='r')
    topic_terms = model.get_topics()
    topic_terms = np.divide(topic_terms, np.sum(topic_terms, axis=1).reshape(-1,1))    # normalize each row to sum to 1
    
    ###############  load src-dst  ###############
    num_perPair = pd.read_csv("./stats_EDU2/num_perPair.csv", index_col=[0])
    pairs = list(num_perPair['src_dst_id'].values)
    unique_ip = list(num_perPair['src_id'].values)
    unique_ip.extend(list(num_perPair['dst_id'].values))
    unique_ip = list(np.unique(unique_ip).astype('int'))
    raw_n = len(unique_ip)
    # print("number of hosts: {}".format(nhost))  # num of src-dst pairs: 386, num of server: 233
    if(nhost<raw_n):
        print("Unsupported! Host number should be no less than {}".format(raw_n))
        sys.exit(0)
    
    dst_dict = {}  # store dst list for each src
    for s in num_perPair['src_id'].values:
        s = int(s)
        dst_dict[s] = list(num_perPair.loc[num_perPair['src_id']==s, 'dst_id'].values.astype('int'))

    ###############  traffic matrix mapping  ###############
    quotient = (nhost+raw_n-1)//raw_n
    remainder = quotient*raw_n - nhost
    id_mat = np.arange(raw_n*quotient).reshape(raw_n, quotient).T
    mute_idx = random.sample(range(raw_n), remainder)
    id_mat[quotient-1][mute_idx] = -1

    ###############  generating  ###############
    inters = []
    new_docs = []
    beta_adj = np.zeros(topic_terms.shape[1])
    for src_ip in dst_dict.keys():
        for epoch in range(quotient):
            src_id = id_mat[epoch][unique_ip.index(src_ip)]
            if(src_id==-1):  # muted src_id
                continue
            timestamp = 0
            while timestamp <time_limit:
                dst_ip = random.sample(dst_dict[src_ip], 1)[0]
                dst_id = id_mat[random.sample(range(quotient), 1)[0]][unique_ip.index(dst_ip)]
                while(dst_id==-1):  # until get an available dst_id
                    dst_id = id_mat[random.sample(range(quotient), 1)[0]][unique_ip.index(dst_ip)]
                
                pair = str(src_ip) + '_' + str(dst_ip)
                i = pairs.index(pair)
                theta = doc_topics[i]
                # sample topic index , i.e. select topic
                z = np.argmax(np.random.multinomial(1, theta))
                # sample word from topic
                beta = topic_terms[z]
                beta_adj[:] = beta[:]
                beta_adj /= (1+5e-8)     # naive approach to fix 'sum(pvals[:-1].astype(np.float64)) > 1.0' precision changes problem when casting
                maxidx = np.argmax(np.random.multinomial(1, beta_adj))  
                new_word = dictionary[maxidx]
                meta = re.split(',|\(|\)', new_word)  # ['', ' 65', '25', '']

                interarrival = sample_time(cdf_interval, int(meta[1])) * 1e9
                interarrival /= get_divider(interarrival, large_interval_threshold, divider, multiplier)
                inters.append(interarrival)
                timestamp += interarrival
                if timestamp > time_limit:
                    break
                flow = [src_id, dst_id, timestamp, sample_size(cdf_size, int(meta[2]))]
                new_docs.append(flow)

    print("#flow nums: {}".format(len(inters)))
    print("realized avg interval: {}, expect interval: {}".format(np.mean(inters), target_interval))
    df = pd.DataFrame(new_docs, columns=['src_id', 'dst_id', 'start_t', 'flow_size'])
    df.sort_values(by=['start_t'], inplace=True)
    # df.to_csv("./flows.csv")
    with open(options.output, "w+") as f:
        src = df['src_id']
        dst = df['dst_id']
        start_t = df['start_t']
        flow_size = (df['flow_size'])
        flow_size = [int(i) for i in flow_size]
        #print(np.sum(flow_size))
        f.write(str(len(src)) + '\n')
        for i in range(len(src)):
            f.write('{} {} 3 100 {} {}\n'.format(src[i], dst[i], flow_size[i], (base_t+start_t[i])*1e-9))
