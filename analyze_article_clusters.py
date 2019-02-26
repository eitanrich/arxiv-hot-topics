import os
import networkx as nx
import numpy as np
import pickle as pkl
import time
import operator
import re
import pickle as pkl
from collections import Counter
from matplotlib import pyplot as plt
from wordcloud import WordCloud
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


def favour_long_terms(count):
    f_count = {k: v * len(re.split(' -', k)) for k, v in count.items()}
    f_sum = float(sum(f_count.values()))
    return {k: v/f_sum for k, v in f_count.items()}


def get_top_n(count, n):
    n = n or len(count)
    sorted_counts = sorted(count.items(), key=lambda kv: -kv[1])[:n]
    return [k.encode('ascii', 'ignore').decode() for k,_ in sorted_counts]


def get_clusters_from_partition(part):
    min_cluster_size = 20       # Ignore clusters smaller than 20 papers
    c = Counter(part.values()).most_common()  # {cluster num: cluster size}
    clusters_list = []
    for c_num, c_size in c:
        if c_size >= min_cluster_size:
            clusters_list.append([k for k, v in part.items() if v == c_num])
    print('Extracted {} significant clusters.'.format(len(clusters_list)))
    return clusters_list


def construct_clusters_list():
    num_sub_partitions = 10     # Number of main clusters that were sub-divided (in citation_graph_clustering.py)
    print('Reading sub clusters...')
    clusters_list = []
    for i in range(num_sub_partitions):
        part = pkl.load(open(r'./data/sub_community_dendogram_{}.p'.format(i), 'rb'))[0]
        print('Sub-clusters of clusters {}: '.format(i), end='')
        clusters_list.extend(get_clusters_from_partition(part))

    print('Main clusters file: ', end='')
    part = pkl.load(open(r'./data/community_dendogram.p', 'rb'))[0]
    # Remove the first num_sub_partitions clusters (already taken):
    large_clusters = [k for k, v in Counter(part.values()).most_common()[:num_sub_partitions]]
    part = {k: v for k, v in part.items() if v not in large_clusters}
    clusters_list.extend(get_clusters_from_partition(part))
    clusters_list.sort(key=len, reverse=True)
    print('Obtained a total of {} clusters with average size of {} papers.'.format(len(clusters_list),
                                                    sum([len(c) for c in clusters_list])//len(clusters_list)))
    return clusters_list


def find_cluster_common_terms(papers):
    cluster_words = []
    for id in papers:
        if id.startswith('ext:'):
            text = id_to_title.get(id, '')
        else:
            text = db[id]['title'] + db[id]['summary']
        tokens = ht.tokenize(text)
        cluster_words += tokens
    common_terms = find_common_terms(cluster_words, 1000)
    common_terms_norm = favour_long_terms(normalize_by_ref(common_terms, corpus_common_terms))
    return common_terms_norm


if __name__ == "__main__":
    print('Reading data...')
    db = pkl.load(open(r'./data/db.p', 'rb'))
    # refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))
    # g = nx.read_gpickle( path = r'./data/citation_network_2.gp')
    # print(len(g.nodes), len(g.edges))

    id_to_title, _ = pkl.load(open(r'./data/all_ids_and_titles.p', 'rb'))
    clusters_list = construct_clusters_list()
    pkl.dump(clusters_list, open(r'./data/clusters_id_list.p', 'wb'))

    print('Reading all text and calculating global corpus common term...')
    corpus_tokens = pkl.load(open(r'./data/total_text.p', 'rb'))
    corpus_common_terms = find_common_terms(corpus_tokens, 10000)
    ht = HotTopics()

    clusters_common_terms_file = open(r'./output/clusters_common_terms.txt', 'w')
    clusters_dir = os.path.join(r'./output/clusters')
    os.makedirs(clusters_dir, exist_ok=True)
    for c_i, papers in enumerate(clusters_list):
        print('Cluster {} - {} papers...'.format(c_i, len(papers)))
        c_dir = os.path.join(clusters_dir, str(c_i))
        os.makedirs(c_dir, exist_ok=True)

        # Write list of papers
        with open(os.path.join(c_dir, 'papers_list.txt'), 'w') as outf:
            for p in papers:
                outf.write('"%s", "%s"\n' % (p, id_to_title.get(p, 'Title not found')))

        # Find common terms
        c_common_terms = find_cluster_common_terms(papers)
        c_top_common_terms = get_top_n(c_common_terms, 50)
        with open(os.path.join(c_dir, 'common_terms.txt'), 'w') as outf:
            for term in c_top_common_terms:
                print(term, file=outf)
        print(c_i, ',', len(papers), ',', c_top_common_terms, file=clusters_common_terms_file)

        # Create word clouds
        wordcloud = WordCloud(max_font_size=60, width=600, height=300).fit_words(c_common_terms)
        wordcloud.to_file(os.path.join(c_dir, 'wordcloud.jpg'))

