import networkx as nx
import os
import pickle
import urllib.request
import json
import time
import random
from collections import Counter
import itertools
WIEGHT_UNIT = 0.01

def load_graph(filename):
    try:
        G = nx.read_gpickle(filename)
    except Exception as e:
        G = nx.Graph()
    return G

## Create a weighted graph of co-authorship ##

def create_author_network(coauthor_file):

    coauthor_graph = nx.Graph()
    add_all_authors(coauthor_graph, db)
    nx.write_gpickle(coauthor_graph, path=coauthor_file)
def add_all_authors(coauthor_graph, db):
        added = 0
        for arxiv_id in sorted(list(db.keys())):
            add_article_authors(coauthor_graph, db[arxiv_id])
            added += 1
            if added == 1000:
                nx.write_gpickle(coauthor_graph, path=coauthor_file)
                added = 0
        print('Done')
def add_article_authors(coauthor_graph, article_data):
        authors = [auth['name'] for auth in article_data['authors']]
        for pair in itertools.combinations(authors, r=2):
            a, other_a = pair
            if coauthor_graph.has_edge(a, other_a):
                coauthor_graph.edges[a, other_a]['weight'] += WIEGHT_UNIT
            else:
                coauthor_graph.add_edge(a, other_a, weight=WIEGHT_UNIT)

## Create a directed citation graph ##
class Article:

    def __init__(self, data):
        self.id = data['arxivId']
        self.authors = [a['name'] for a in data['authors']]
        self.title = data['title']
        self.year = data['year']
        self.venue = data['venue']
        #self.isInfluential = data['isInfluential'] #does not appear in json data

def get_article(data):
    for article in article_graph.nodes:
        if article.id == data['arxivId']:
            return article
    return Article(data)

def add_out_neighbors(json_data, curr):
    '''
    add articles that curr references
    '''
    for referenced_article_data in json_data['references']:
        if referenced_article_data['arxivId']:
            ref_article = get_article(referenced_article_data)
            article_graph.add_edge(curr, ref_article)
    print('{} references {} papers'.format(curr.id, len(json_data['references'])))

def add_in_neighbors(json_data, curr):
    '''
    add articles that cite curr
    '''
    for citing_article_data in json_data['citations']:
        if citing_article_data['arxivId']:
            citing_article = get_article(citing_article_data)
            article_graph.add_edge(citing_article, curr)
    print('{} cited by {} papers'.format(curr.id, len(json_data['citations'])))

def update_article_graph(json_data):
    curr = Article(json_data)
    add_out_neighbors(json_data, curr)  # articles referenced by paper
    add_in_neighbors(json_data, curr)  # articles that cited the paper
    return

def query_all(db):
    '''
    get citation data from semantic scholar for all articles in db
    '''
    queried = Counter()
    query_count = 0
    num_added = 0
    for arxiv_id in sorted(list(db.keys())):
        if queried[arxiv_id]: #already queried this article
            continue
        queried[arxiv_id] = True
        query_count += 1
        got_response = query_article(arxiv_id)
        if got_response:
            num_added += 1
        if query_count%10 == 0:
            time.sleep(random.uniform(3, 5))
        if num_added%100 == 0:
            print('already added', num_added)
    print('Done')

def query_article(arxiv_id):
    query_id = arxiv_id if '.' in arxiv_id else 'cs/' + arxiv_id
    query_url = 'https://api.semanticscholar.org/v1/paper/arXiv:' + query_id + '?include_unknown_references=true'
    try:
        with urllib.request.urlopen(query_url) as url:
            response = url.read()
    except Exception as e:
        print('Paper {} not found in Semantic Scholar - skipping'.format(arxiv_id))
        response = {}
    if response:
        json_data = json.loads(response)
        update_article_graph(json_data)
        return True
    return False

if __name__ == "__main__":
    article_graph = nx.DiGraph()
    db_file = r'./data/db2.p'
    citation_network_file = r'./data/citation_network.gp'
    coauthor_file = r'./data/citation_network.gp'
    print(os.getcwd())
    db = pickle.load(open(db_file, 'rb'))
    query_all(db)
    nx.write_gpickle(G = article_graph, path = citation_network_file)

