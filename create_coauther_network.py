import networkx as nx
import itertools
import pickle
from matplotlib import pyplot as plt
from utils import safe_pickle_dump
import matplotlib.cm as cmx
UNIT = 0.01

def add_all(db):
    added = 0
    for arxiv_id in sorted(list(db.keys())):
        add_article_authors(db[arxiv_id])
        added += 1
        if added == 1000:
            nx.write_gpickle(coauthor_graph, path = coauthor_file)
            added = 0
    print('Done')

def add_article_authors(article_data):
    authors = [auth['name'] for auth in article_data['authors']]
    for pair in itertools.combinations(authors, r=2):
        a, other_a = pair
        if coauthor_graph.has_edge(a, other_a):
            coauthor_graph.edges[a, other_a]['weight'] += UNIT
        else:
            coauthor_graph.add_edge(a, other_a, weight=UNIT)

def load_graph(filename):
    try:
        G = nx.read_gpickle(filename)
    except Exception as e:
        G = nx.Graph()
    return G

if __name__ == "__main__":
    db_file = r'./data/db.p'
    coauthor_file = r'./data/citation_network.gp'
    adjlist_file = r'./test.adjlist'
    # print(os.getcwd())
    db = pickle.load(open(db_file, 'rb'))
    coauthor_graph = load_graph(coauthor_file)
    #coauthor_graph = nx.Graph()
    #add_all(db)
    nx.write_gpickle(coauthor_graph, path = coauthor_file)
