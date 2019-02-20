import os
import networkx as nx
import community        # pip install python-louvain
import numpy as np
import pickle as pkl
import time
from matplotlib import pyplot as plt


if __name__ == "__main__":
    print('Reading data...')
    # refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))
    # db = pkl.load(open(r'./data/db.p', 'rb'))
    g = nx.read_gpickle( path = r'./data/citation_network_2.gp')
    print(len(g.nodes), len(g.edges))

    print('Reducing the graph size...')
    p_sebset = [id for id in g.nodes() if g.degree(id) > 4 or not id.startswith('ext:')]
    g = g.subgraph(p_sebset)
    print(len(g.nodes), len(g.edges))

    print('Finding best_partition...')
    g_u = g.to_undirected()
    part = community.best_partition(g_u, resolution=10.)
    print('Saving...')
    pkl.dump(part, open(r'./data/best_partition_part.p', 'wb'))
    # part = pkl.load(open(r'./data/best_partition_part.p', 'rb'))


    # print('weakly_connected_components:')
    # for i, cc in enumerate(sorted(nx.weakly_connected_components(g), key=len, reverse=True)):
    #     print(i, len(cc))
    #     if len(cc) < 10:
    #         break

    # print('Trying to find communities...')
    # comp = community.centrality.girvan_newman(g)
    # l0 = tuple(sorted(c) for c in next(comp))
    #
    # print('Betweenness...')
    # betweenness = nx.betweenness_centrality(g)
    # plt.hist(list(betweenness.values()), bins=50)
    # plt.show()


    # Demo with two different topics
    # def is_t1_title(title):
    #     return 'adversarial examples' in title.lower()
    #
    # def is_t2_title(title):
    #     return 'q learning' in title.lower() or 'q-learning' in title.lower()
    #
    #
    # print('Searching for GAN papers...')
    # t1_papers = [id for id, node in g.nodes.items() if is_t1_title(node['title'])]
    # t2_papers = [id for id, node in g.nodes.items() if is_t2_title(node['title'])]
    # print(len(t1_papers), len(t2_papers), 'relevant papers')
    # g_topic = g.subgraph(t1_papers + t2_papers)
    #
    # for i, cc in enumerate(sorted(nx.weakly_connected_components(g_topic), key=len, reverse=True)):
    #     print(len(cc), len([p for p in t1_papers if p in cc]), len([p for p in t2_papers if p in cc]))
    #     if i==0:
    #         cc_0_papers = [p for p in cc]
    #     if len(cc)<10:
    #         break
    #
    # colors = np.ones(len(g_topic.nodes))
    # is_ext = [v.startswith('ext:') for v in g_topic.nodes()]
    # is_cc0 = [v in cc_0_papers for v in g_topic.nodes()]
    # is_t1 = [v in t1_papers for v in g_topic.nodes()]
    # colors[is_t1] = 0
    # nx.draw(g_topic, with_labels=False, alpha=0.5, node_size=150, node_color=colors, cmap='jet')
    # plt.show()

