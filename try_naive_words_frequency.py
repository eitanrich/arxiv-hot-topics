import os
import pickle
import re
import numpy as np
from utils import safe_pickle_dump
from collections import defaultdict
from matplotlib import pyplot as plt

if __name__ == "__main__":
    db_file = r'./data/db.p'

    db = pickle.load(open(db_file, 'rb'))
    print('Loaded basic metadata of {} papers.'.format(len(db)))

    counts = defaultdict(int)

    print('Scanning abstracts...')
    paper_num = 0
    for pid, metadata in db.items():
        for w in metadata['summary'].split():
            w = re.sub('[\.\,\-\{\}\(\)]', '', w).lower()
            counts[w] += 1
        paper_num += 1
        if paper_num%100 == 0:
            print(paper_num)

    print('Total of {} unique words counted.'.format(len(counts)))

    words = list(counts.keys())
    freq = list(counts.values())
    order = np.argsort(freq)
    print('Most common words (descending order):')
    for i in range(1, 1000):
        print(words[order[-i]], ', ', end='')
        if i%10 == 0:
            print()
    # plt.plot(np.log(np.array(freq)[order]))
    # plt.ylabel('Log frequency')
    # plt.show()
    # print('Done')
