import pickle
from utils import safe_pickle_dump

cats = ['cs.CV', 'cs.AI', 'cs.LG', 'cs.CL', 'cs.NE', 'stat.ML']
db = {}
for cat in cats:
    with open(r'./data/db.'+cat+'.p', 'rb') as f:
        cat_db = pickle.load(f)
    years = sorted([p['published'] for p in cat_db.values()])
    print('Category {}: {} papers from {} to {}.'.format(cat, len(cat_db), years[0], years[-1]))
    db = {**db,  **cat_db}
print('Total number of papers:', len(db))
print('Dumping...')
safe_pickle_dump(db, r'./data/db.p')
