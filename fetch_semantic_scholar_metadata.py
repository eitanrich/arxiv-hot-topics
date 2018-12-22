import os
import pickle
import argparse
import urllib.request
import json
import time
import random
from utils import safe_pickle_dump

def dump_refs(file_name, references):
    print('Saving references file with entries for {} papers'.format(len(references)))
    safe_pickle_dump(references, file_name)


if __name__ == "__main__":
    db_file = r'./data/db.p'
    refs_file = r'./data/refs_db.p'

    print(os.getcwd())
    db = pickle.load(open(db_file, 'rb'))
    print('Loaded basic metadata of {} papers.'.format(len(db)))

    try:
        references = pickle.load(open(refs_file, 'rb'))
    except Exception as e:
        references = {}
    print('{} papers already have listed references'.format(len(references)))

    query_count = 0
    num_added_refs = 0
    for arxiv_id in sorted(list(db.keys())):
        if arxiv_id in references:
            continue
        query_count += 1

        query_url = 'https://api.semanticscholar.org/v1/paper/arXiv:' + arxiv_id + '?include_unknown_references=true'
        try:
            with urllib.request.urlopen(query_url) as url:
                response = url.read()
        except Exception as e:
            print('Paper {} not found in Semantic Scholar - skipping'.format(arxiv_id))
            references[arxiv_id] = []
            response = []

        if response:
            json_data = json.loads(response)
            refs = []
            for ref in json_data['references']:
                authors = [a['name'] for a in ref['authors']]
                refs.append({'arxivId': ref['arxivId'],
                             'title': ref['title'],
                             'year': ref['year'],
                             'authors': authors})
            references[arxiv_id] = refs
            num_added_refs += 1
            print('Found {} references for {}'.format(len(refs), arxiv_id))

        if query_count%10 == 0:
            time.sleep(random.uniform(3, 5))

        if num_added_refs%100 == 0:
            dump_refs(refs_file, references)

    dump_refs(refs_file, references)
    print('Done')
