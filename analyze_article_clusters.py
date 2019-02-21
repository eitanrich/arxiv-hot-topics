import os
import networkx as nx
import numpy as np
import pickle as pkl
import time
import operator
import pickle as pkl
from collections import Counter
from matplotlib import pyplot as plt
from identify_hot_topics import HotTopics, get_bigrams, get_trigrams


def find_common_terms(tokens, num_terms):
    terms = tokens + get_bigrams(tokens) + get_trigrams(tokens)
    common_terms = Counter(terms).most_common(num_terms)
    sum_common_terms = float(sum([v for _,v in common_terms]))
    return {k: v/sum_common_terms for k, v in common_terms}


def normalize_by_ref(count, ref_count):
    ref_min = min(ref_count.values())
    rel_count = {k: v/ref_count.get(k, ref_min) for k, v in count.items()}
    rel_sum = float(sum(rel_count.values()))
    return {k: v/rel_sum for k, v in rel_count.items()}


def get_top_n(count, n):
    n = n or len(count)
    sorted_counts = sorted(count.items(), key=lambda kv: -kv[1])[:n]
    return [k.encode("utf-8") for k,_ in sorted_counts]


if __name__ == "__main__":
    print('Reading data...')
    # refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))
    db = pkl.load(open(r'./data/db.p', 'rb'))
    # g = nx.read_gpickle( path = r'./data/citation_network_2.gp')
    # print(len(g.nodes), len(g.edges))

    id_to_title, _ = pkl.load(open(r'./data/all_ids_and_titles.p', 'rb'))

    dendo = pkl.load(open(r'./data/community_dendogram.p', 'rb'))
    part = dendo[0]
    print(type(part), len(part), max(part.values()))


    # Order the partition from larger to smaller
    c = Counter(part.values())
    c_order = np.argsort(list(c.values()))[::-1]
    with open(r'./output/community_clusters.txt', 'w') as outf:
        for i in range(c_order.size):
            papers = [id for id, p in part.items() if p==c_order[i]]
            print('Cluster {} - {} papers'.format(i, len(papers)))
            outf.write('\n************** Cluster {} - {} papers **************\n'.format(i, len(papers)))
            for j in range(min(len(papers), 100)):
                outf.write('%10s: %s\n' % (papers[j], id_to_title.get(papers[j], 'NOT FOUND')))
            if len(papers) < 10:
                break

    # Find common terms
    print('Reading all text and calculating global corpus common term...')
    corpus_tokens = pkl.load(open(r'./data/total_text.p', 'rb'))
    corpus_common_terms = find_common_terms(corpus_tokens, 10000)

    ht = HotTopics()
    with open(r'./output/community_clusters_common_terms.txt', 'w') as outf:
        for i in range(c_order.size):
            papers = [id for id, p in part.items() if p==c_order[i]]
            print('Cluster {} - {} papers:'.format(i, len(papers)))
            print('Cluster {} - {} papers:'.format(i, len(papers)), file=outf)
            cluster_words = []
            for id in papers:
                if id.startswith('ext:'):
                    text = id_to_title.get(id, '')
                else:
                    text = db[id]['title'] + db[id]["summary"]
                tokens = ht.tokenize(text)
                cluster_words += tokens
            common_terms = find_common_terms(cluster_words, 1000)
            # print(get_top_n(common_terms, 100))
            common_terms_norm = normalize_by_ref(common_terms, corpus_common_terms)
            print(get_top_n(common_terms_norm, 50), file=outf)
            if len(papers) < 10:
                break
