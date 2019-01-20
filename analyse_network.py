import networkx as nx
import pickle
import itertools
import matplotlib.pyplot as plt
from matplotlib import colors, colorbar
from plotly import graph_objs as go
import plotly.plotly as ply
import plotly.tools as tls
from networkx.algorithms import community
import numpy as np
MAX_PLOTS = 50
class Article:
    def __init__(self, data):
        self.id = data['arxivId']
        self.authors = [a['name'] for a in data['authors']]
        self.title = data['title']
        self.year = data['year']
        self.venue = data['venue']
        #self.isInfluential = data['isInfluential'] #does not appear in json data


def get_relevant_connected_component(graph):
    count = 0
    for nodeset in nx.weakly_connected_components(graph):
       if len(nodeset) > 50:
           subgraph = graph.subgraph(nodeset)
           new  = nx.DiGraph()
           new.add_nodes_from(nodeset)
           new.add_edges_from(subgraph.edges)
           #nx.write_gexf(subgraph, r'./data/citenet_cc' + str(count) + 'gexf')
           nx.write_gpickle(new, r'./data/citation_network_compenent_' + str(count) + '.gp')
           count += 1
           print(count)

def get_weakly_cc(G, node):
    """ get weakly connected component of node"""
    for cc in nx.weakly_connected_components(G):
        if node in cc:
            return cc
    else:
        return set()

def self_citation_counts(G):
    counts = []
    for n, nbrsdict in G.adjacency():
        authors = n.authors
        for nbr, eattr in nbrsdict.items():
            common_authors = authors.intersect(nbr.authors)
            counts.append(len(common_authors))
    return counts

def plot_unweighted_graph(graph, title = "", with_labels = True, path = r'./data/citenet.png'):
    fig, ax = plt.subplots()
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, node_color='r', node_size=2, edgelist=graph.edges, width=0.8,
            with_labels=with_labels, font_size=8)
    plt.title(title)
    ax.axis('off')
    plt.show()
    return True

def plot_weighted_graph(graph, plot_count, title = "",  with_labels = True):
    MAX_NODES_TO_LABEL = 80
    MAX_NODES_TO_PLOT = 400
    MIN_NODES_TO_PLOT = 10
    fig, ax = plt.subplots()
    edges, weights = zip(*nx.get_edge_attributes(graph, 'weight').items())
    if len(set(weights)) < 4:
        print("not interesting enough, not plotting")
        return False
    # make a color map of fixed colors
    cdict = {0.01:'royalblue', 0.02 : 'deepskyblue', 0.03: 'turquoise', 0.04: 'springgreen',
            0.05 : 'yellow', 0.06: 'gold', 0.07 : 'goldenrod', 0.08 : 'orange', 0.09: 'coral',
            0.1 :'salmon', 0.11 : 'tomato', 0.12 : 'indianred', 0.13 : 'deeppink'}
    pos = nx.spring_layout(graph)
    if nx.number_of_nodes(graph) > MAX_NODES_TO_LABEL:
        with_labels = False
    if nx.number_of_nodes(graph) < MIN_NODES_TO_PLOT:
        print('not enough nodes, not plotting')
        return False
    if nx.number_of_nodes(graph)  > MAX_NODES_TO_PLOT:
        print("too many nodes, not plotting")
        return False
    edge_colors = [cdict[w] for w in weights]
    cmap = colors.ListedColormap([cdict[w] for w in sorted(list(set(weights)))])
    nx.draw(graph, pos, node_color='r', node_size=2, edgelist=edges, edge_color=edge_colors, width=0.8,
         with_labels=with_labels, font_size = 8)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=100*max(weights)))
    sm.set_array([])
    plt.colorbar(sm, label = 'number of articles co-authored', ticks=[k for k in range(int(100*max(weights)) + 1)])
    print('wieghts are: ', weights)
    plt.title(title)
    ax.axis('off')
    plt.savefig(r'./data/co-author_graph'+str(plot_count)+'.png')
    return True

def plot_subgraph(sub_graph, title, plot_count, weighted = True):
    if weighted:
        return plot_weighted_graph(sub_graph, plot_count, title)
    else:
        return plot_unweighted_graph(sub_graph, title)

def plot_all_subgraphs(G, directed = False, weighted = True):
    plot_count = 20
    for n, nbrsdict in G.adjacency():
        if plot_count > MAX_PLOTS:
            return
        if not directed:
            sub_graph = G.subgraph(nx.node_connected_component(G, n))
        else:
            sub_graph = G.subgraph(get_weakly_cc(G, n))
        plotted = plot_subgraph(sub_graph, "co-author network", plot_count ,weighted)
        if plotted:
            plot_count += 1

def filter_graph(G, min_degree = 2):
    '''
    iteratively remove nodes that only have one edge
    '''
    def get_nodes_to_remove():
        return [node for node in G.nodes if (G.in_degree(node) + G.out_degree(node) < 2)]
    to_remove = get_nodes_to_remove()
    while len(to_remove) > 0:
        G.remove_nodes_from(to_remove)
        to_remove = get_nodes_to_remove()
    return G

def plot_degree_distribution(G):
    mpl_fig = plt.figure()
    mpl_fig.add_subplot(111)
    nodes = G.nodes
    indegree = [G.in_degree(n) for n in nodes if G.in_degree(n)]
    outdegree = [G.out_degree(n) for n in nodes if G.out_degree(n)]
    bins = [k for k in range(max(max(outdegree), max(outdegree)))]
    plt.hist(indegree, bins, alpha=0.5, label='in degree')
    plt.hist(outdegree, bins, alpha=0.5, label='out degree')
    plt.legend(loc='upper right')
    plt.title('citation network, distribution of degree')
    plt.savefig(r'./data/citenet_degreedist.png')

def plot_betweenness(G):
    mpl_fig = plt.figure()
    mpl_fig.add_subplot(111)
    betweenes = nx.betweenness_centrality(G)
    betweenes_vals = list(betweenes.values())
    bins = [k for k in range(len(set(betweenes_vals)))]
    plt.hist(betweenes_vals, bins, alpha=0.5, label='betweenness')
    plt.legend(loc='upper right')
    plt.title('citation network, distribution of betweenness value')
    plt.savefig(r'./data/citenet_betweennes_dist.png')

def has_arxiv_neighbor(refs_db, arxiv_id):
    neighbors = refs_db[arxiv_id]
    for n in neighbors:
        if n['arxivId']:
            return True
    return False

def partition(G):
    partition_iterator = community.girvan_newman(G)
    return

if __name__ == "__main__":
    db_file = r'./data/db.p'
    refs_db_file = r'./refs_db.p'
    network_file = r'./data/citation_network_largest_component.gp'
    G = nx.read_gpickle(path = network_file)
    print(nx.info(G))
    plot_betweenness(G)
