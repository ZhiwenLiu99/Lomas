import os
import re
import numpy as np
import pandas as pd
from optparse import OptionParser

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

if __name__ == "__main__":
    np.random.seed(2022)
    parser = OptionParser()
    parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 3000", default = "3000")
    parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "tmp_traffic.txt")
    options,args = parser.parse_args()

    time_limit = float(options.time)  # 时间窗口大小
    nhost = None          # 节点数量（默认值）
    load = None           # 平均流量load（默认值）

    ###############  load model  ###############
    dictionary = corpora.Dictionary.load("./model_EDU2/qzone.dict")      
    doc_topics = pd.read_csv("./model_EDU2/res_document_topics.csv", index_col=[0]).values  # document-topic matrix
    doc_topics = np.divide(doc_topics, np.sum(doc_topics, axis=1).reshape(-1,1))       # normalize each row to sum to 1
    model = LdaModel.load("./model_EDU2/qzone.model", mmap='r')
    topic_terms = model.get_topics()
    topic_terms = np.divide(topic_terms, np.sum(topic_terms, axis=1).reshape(-1,1))    # normalize each row to sum to 1

    ###############  load cdf  ###############
    cdf_size = pd.read_csv("./stats_EDU2/cdf_size.csv", index_col=[0])
    cdf_interval = pd.read_csv("./stats_EDU2/cdf_interval.csv", index_col=[0])
    
    ###############  load src-dst  ###############
    num_perPair = pd.read_csv("./stats_EDU2/num_perPair.csv", index_col=[0])
    pairs = num_perPair['src_dst_id'].values
    unique_ip = list(num_perPair['src_id'].values)
    unique_ip.extend(list(num_perPair['dst_id'].values))
    unique_ip = list(np.unique(unique_ip).astype('int'))
    nhost = len(unique_ip)
    # print("number of hosts: {}".format(nhost))  # num of src-dst pairs: 386, num of server: 233

    import pdb
    pdb.set_trace()

    new_docs = []
    this_topic = np.zeros(topic_terms.shape[1])
    for i in range(len(pairs)):
        flow_id = 0
        timestamp = 0
        pair = pairs[i]
        theta = doc_topics[i]
        # print("--------------- pair: {}, start: {}, end: {} ---------------".format(pair, timestamp, time_limit))
        while timestamp<time_limit:
            # sample topic index , i.e. select topic
            z = np.argmax(np.random.multinomial(1, theta))
            # sample word from topic
            beta = topic_terms[z]
            this_topic[:] = beta[:]
            this_topic /= (1+1e-7)  # to avoid sum(pval)>1 because of decimal round
            maxidx = np.argmax(np.random.multinomial(1, this_topic))
            new_word = dictionary[maxidx]
            meta = re.split(',|\(|\)', new_word)  # ['', ' 65', '25', '']

            src_id = unique_ip.index(int(pair.split('_')[0]))
            dst_id = unique_ip.index(int(pair.split('_')[1]))
            interarrival = sample_time(cdf_interval, int(meta[1]))
            timestamp += interarrival
            flow = [src_id, dst_id, timestamp, sample_size(cdf_size, int(meta[2]))]
            new_docs.append(flow)
            flow_id += 1

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
            f.write('{} {} 3 100 {} {}\n'.format(src[i], dst[i], flow_size[i], 2 + start_t[i]))
