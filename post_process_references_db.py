import os
import networkx as nx
import pickle as pkl
import string
import numpy as np
from collections import Counter
from matplotlib import pyplot as plt


def normalize(text):
    remove_chars = [".", ",", "(", ")", "{", "}", "[", "]", "$", "?", "\\", ":", "'", '"', ";", "`", "mathbf", "\n"]
    for char in remove_chars:
        text = text.replace(char, "")
    text = text.replace("  ", " ")
    text = text.replace("-", " ")
    text = ''.join(filter(lambda x: x in string.printable, text))
    return text.title()

if __name__ == "__main__":
    print('Reading data...')
    db = pkl.load(open(r'./data/db.p', 'rb'))
    print(len(db), 'papers read.')
    some_id = list(db.keys())[10000]

    print('collecting paper titles and first authors...')
    all_titles = {k: normalize(p['title']) for k, p in db.items()}
    print(list(all_titles.values())[:30])
    print(len(all_titles.values()), len(set(all_titles.values())))
    title_to_id = {t: i for i, t in all_titles.items()}

    print('Now working on the refs...')
    refs_db = pkl.load(open(r'./data/refs_db.p', 'rb'))
    print('Ref keys:', refs_db[some_id][0].keys())
    # all_ref_ids = [[r['arxivId'] for r in r_list] for r_list in refs_db.values()]
    all_ref_ids = [r['arxivId'] for r_list in refs_db.values() for r in r_list]
    print(len(all_ref_ids), 'refs found, out of which', all_ref_ids.count(None), 'have no arXiv ID')
    all_ref_titles = [normalize(r['title']) for r_list in refs_db.values() for r in r_list]
    all_ref_id_from_title = [title_to_id.get(t) for t in all_ref_titles]
    print(len(all_ref_id_from_title), 'refs found, out of which', all_ref_id_from_title.count(None), 'arXiv title not found')
    print('Number of unique ref titles:', len(set(all_ref_titles)))
    ref_titles, ref_nums = zip(*Counter(all_ref_titles).items())
    ref_nums = np.array(list(ref_nums))
    print(ref_nums.shape, np.min(ref_nums), np.max(ref_nums), np.mean(ref_nums))
    print(ref_titles[np.argmax(ref_nums)], np.max(ref_nums))
    plt.hist(ref_nums, bins=np.arange(100))
    plt.yscale('log', nonposy='clip')
    plt.title('Number of citations per title')
    plt.show()
    print()
