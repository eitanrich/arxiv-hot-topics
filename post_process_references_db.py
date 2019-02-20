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

if __name__ == "__main__":
    print('Reading data...')
    db = pkl.load(open(r'./data/db.p', 'rb'))
    print(len(db), ' arXiv papers read.')
    some_id = list(db.keys())[10000]

    print('Now collecting all referenced titles...')
    refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))

    id_to_title, title_to_id = collect_ids_and_titles(db, refs_db)

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
            dst_id = r['arxivId'] or title_to_id[normalize(r['title'])]
            article_graph.add_edge(src_id, dst_id)

    print('Saving...')
    nx.write_gpickle(G = article_graph, path = r'./data/citation_network_2.gp')


    # print('Reading data...')
    # db = pkl.load(open(r'./data/db.p', 'rb'))
    # print(len(db), 'papers read.')
    # some_id = list(db.keys())[10000]
    #
    # print('collecting paper titles and first authors...')
    # all_titles = {k: normalize(p['title']) for k, p in db.items()}
    # print(list(all_titles.values())[:30])
    # print(len(all_titles.values()), len(set(all_titles.values())))
    # title_to_id = {t: i for i, t in all_titles.items()}
    #
    # print('Now working on the refs...')
    # refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))
    # print('Ref keys:', refs_db[some_id][0].keys())
    # # all_ref_ids = [[r['arxivId'] for r in r_list] for r_list in refs_db.values()]
    # all_ref_ids = [r['arxivId'] for r_list in refs_db.values() for r in r_list]
    # print(len(all_ref_ids), 'refs found, out of which', all_ref_ids.count(None), 'have no arXiv ID')
    # all_ref_titles = [normalize(r['title']) for r_list in refs_db.values() for r in r_list]
    # all_ref_id_from_title = [title_to_id.get(t) for t in all_ref_titles]
    # print(len(all_ref_id_from_title), 'refs found, out of which', all_ref_id_from_title.count(None), 'arXiv title not found')
    # print('Number of unique ref titles:', len(set(all_ref_titles)))
    # ref_titles, ref_nums = zip(*Counter(all_ref_titles).items())
    # ref_nums = np.array(list(ref_nums))
    # print(ref_nums.shape, np.min(ref_nums), np.max(ref_nums), np.mean(ref_nums))
    # print(ref_titles[np.argmax(ref_nums)], np.max(ref_nums))
    # plt.hist(ref_nums, bins=np.arange(100))
    # plt.yscale('log', nonposy='clip')
    # plt.title('Number of citations per title')
    # plt.show()
    # print()
