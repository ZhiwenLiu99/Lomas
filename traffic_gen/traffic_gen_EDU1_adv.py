# -*- coding: utf-8 -*

import sys
import os
import re
import pickle
import numpy as np
import pandas as pd

from gensim import corpora
from gensim.models import LdaModel


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
    if (length > threshold):
        return param * divider 
    else:
        return param * divider * (length / threshold) ** 2
    

if __name__ == "__main__":
    np.random.seed(2022)
    
    time_limit = float(sys.argv[1]) # 时间窗口大小s 默认3000
    target_interval = float(sys.argv[2])
    param = float(sys.argv[3])
    divider = 1
    large_interval_threshold = 3 # 大于3s的时间窗口，认为是大时间窗口，作为除的对象
    nhost = None          # 节点数量（默认值）默认None
    load = None           # 平均流量load（默认值）

    ###############  load model  ###############
    dictionary = corpora.Dictionary.load("./model/qzone.dict")      
    doc_topics = pd.read_csv("./model/res_document_topics.csv", index_col=[0]).values  # document-topic matrix
    doc_topics = np.divide(doc_topics, np.sum(doc_topics, axis=1).reshape(-1,1))       # normalize each row to sum to 1
    model = LdaModel.load("./model/qzone.model", mmap='r')
    topic_terms = model.get_topics()
    topic_terms = np.divide(topic_terms, np.sum(topic_terms, axis=1).reshape(-1,1))    # normalize each row to sum to 1

    ###############  load cdf  ###############
    cdf_size = pd.read_csv("./stats/cdf_size.csv", index_col=[0])
    cdf_interval = pd.read_csv("./stats/cdf_interval.csv", index_col=[0])
    # with open("cdf.txt", "w") as f:
    #     for i in range(len(cdf_size['cdf'])):
    #         f.write(str(cdf_size['cdf'][i]) + ' ' + str(cdf_size['percentile'][i]) + '\n')
    # for i in range(len(cdf_interval['cdf'])):
    #     cdf_interval['cdf'][i] /= divider
    #倍增interval使得合法
    #get_mean_from_cdf(cdf_interval)
    ###############  load src-dst  ###############
    num_perPair = pd.read_csv("./stats/num_perPair.csv", index_col=[0])
    pairs = num_perPair['src_dst_id'].values
    unique_ip = list(num_perPair['src_id'].values)
    unique_ip.extend(list(num_perPair['dst_id'].values))
    unique_ip = list(np.unique(unique_ip).astype('int'))
    nhost = len(unique_ip)
    print("time: {}".format(time_limit))
    print("#pairs: {} #hosts: {}".format(len(pairs), nhost))
    mean = 14.22288312336819
    divider = mean / target_interval 
    #print("avg interval: {} , divider= {}".format(mean, divider))
    new_docs = []
    this_topic = np.zeros(topic_terms.shape[1])
    inters = []
    for i in range(len(pairs)):
        flow_id = 0
        timestamp = 0
        pair = pairs[i]
        theta = doc_topics[i]
        # print("--------------- pair: {}, start: {}, end: {} ---------------".format(pair, timestamp, time_limit))
        while timestamp <time_limit:
            # sample topic index , i.e. select topic
            z = np.argmax(np.random.multinomial(1, theta))
            # sample word from topic
            beta = topic_terms[z]
            maxidx = np.argmax(np.random.multinomial(1, beta))
            new_word = dictionary[maxidx]
            meta = re.split(',|\(|\)', new_word)  # ['', ' 65', '25', '']

            src_id = unique_ip.index(int(pair.split('_')[0]))
            dst_id = unique_ip.index(int(pair.split('_')[1]))
            interarrival = sample_time(cdf_interval, int(meta[1]))
            interarrival /= get_divider(interarrival, large_interval_threshold, divider, param)
            inters.append(interarrival)
            timestamp += interarrival
            if timestamp > time_limit:
                break
            flow = [src_id, dst_id, timestamp, sample_size(cdf_size, int(meta[2]))]
            new_docs.append(flow)
            flow_id += 1
    print("#flow: {}".format(len(inters)))
    print("actual mean: {} expect: {}".format(np.mean(inters), target_interval))
    df = pd.DataFrame(new_docs, columns=['src_id', 'dst_id', 'start_t', 'flow_size'])
    df.sort_values(by=['start_t'], inplace=True)
    #df.to_csv("./flows.csv")
    with open("./data/model.data", "w") as f:
        src = df['src_id']
        dst = df['dst_id']
        start_t = df['start_t']
        flow_size = (df['flow_size'])
        flow_size = [int(i) for i in flow_size]
        #print(np.sum(flow_size))
        f.write(str(len(src)) + '\n')
        for i in range(len(src)):
            f.write('{} {} 3 100 {} {}\n'.format(src[i], dst[i], flow_size[i], 2 + start_t[i]))
    # import pdb
    # pdb.set_trace()
