import os
import networkx as nx
import pickle as pkl
import string
import numpy as np
from collections import Counter
from matplotlib import pyplot as plt
# from utils import Article


def normalize(text):
    remove_chars = [".", ",", "(", ")", "{", "}", "[", "]", "$", "?", "\\", ":", "'", '"', ";", "`", "mathbf", "\n"]
    for char in remove_chars:
        text = text.replace(char, "")
    text = text.replace("  ", " ")
    text = text.replace("-", " ")
    text = ''.join(filter(lambda x: x in string.printable, text))
    return text.title()


def collect_ids_and_titles(db, refs_db):
    ids_and_titles_file = r'./data/all_ids_and_titles.p'
    if os.path.isfile(ids_and_titles_file):
        print('Loading from', ids_and_titles_file)
        return pkl.load(open(ids_and_titles_file, 'rb'))

    print('collecting arXiv paper titles...')
    arxiv_id_to_titles = {k: normalize(p['title']) for k, p in db.items()}
    arxiv_title_to_id = {t: i for i, t in arxiv_id_to_titles.items()}
    print('Collecting referenced titles...')
    all_ref_titles = set([normalize(r['title']) for r_list in refs_db.values() for r in r_list])
    all_titles = list(all_ref_titles | set(arxiv_id_to_titles.values()))
    print('A total of', len(all_titles), 'titles found')
    print('Now creating id-to-title maps with running ext:id for external titles...')
    running_ext_ids = ['ext:{}'.format(i) for i in range(len(all_titles))]
    id_to_title = {arxiv_title_to_id.get(all_titles[i], running_ext_ids[i]): all_titles[i] for i in range(len(all_titles))}
    title_to_id = {t: i for i, t in id_to_title.items()}
    print('Saving...')
    pkl.dump((id_to_title, title_to_id), open(ids_and_titles_file, 'wb'))
    return id_to_title, title_to_id


def create_id_to_year():
    arxiv_id_to_year = {k: int(p['published'][:4]) for k, p in db.items()}
    ext_title_to_year = {normalize(r['title']): int(r['year'] or -1) for r_list in refs_db.values() for r in r_list}
    ext_id_to_year = {k: ext_title_to_year.get(t, -1) for k, t in id_to_title.items() if k.startswith('ext:')}
    id_to_year = {**arxiv_id_to_year, **ext_id_to_year}
    id_to_year = {k: (v if v > 1900 else 0) for k, v in id_to_year.items()}
    pkl.dump(id_to_year, open(r'./data/all_ids_to_years.p', 'wb'))


if __name__ == "__main__":
    print('Reading data...')
    db = pkl.load(open(r'./data/db.p', 'rb'))
    print(len(db), ' arXiv papers read.')
    some_id = list(db.keys())[10000]

    print('Now collecting all referenced titles...')
    refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))

    id_to_title, title_to_id = collect_ids_and_titles(db, refs_db)

    # create_id_to_year()
    # exit()

    print('Creating the graph...')
    article_graph = nx.DiGraph()

    print('Adding arXiv nodes...')
    for id, data in db.items():
        article_graph.add_node(id, title=data['title'])

    print('Adding external nodes...')
    for id, title in id_to_title.items():
        if id.startswith('ext:'):
            article_graph.add_node(id, title=title)

    print('Adding all references...')
    for src_id, refs in refs_db.items():
        for r in refs:
            dst_id = title_to_id[normalize(r['title'])]
            assert src_id in article_graph.nodes and dst_id in article_graph.nodes
            article_graph.add_edge(src_id, dst_id)

    print('Saving...')
    nx.write_gpickle(G = article_graph, path = r'./data/citation_network_2.gp')

