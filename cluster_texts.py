import string
import nltk
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from pprint import pprint
nltk.download('punkt')

def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    text = text.translate(None, string.punctuation)
    tokens = word_tokenize(text)

    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]

    return tokens

def tokenize(text):
    import re
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

def cluster_texts(texts):
    vectorizer = TfidfVectorizer(tokenizer=tokenize,
                                 stop_words=stopwords.words('english'),
                                 max_df=0.5,
                                 min_df=0.1,
                                 lowercase=True)
    X = vectorizer.fit_transform(texts)

    k = 40
    model = KMeans(n_clusters= k, init='k-means++', max_iter=100, n_init=1)
    model.fit(X)

    clustering = {}

    for idx, label in enumerate(model.labels_):
        if label not in clustering:
            clustering[label] = []
        clustering[label].append(idx)

    return clustering

def export_cluster_to_vos(cluster_num):
    import export_to_vos
    mini_db = {}
    for item in clusters[cluster_num]:
        mini_db[ids[item]] = db[ids[item]]
    export_to_vos.write(mini_db, 'cluster_text_' + str(cluster_num)+ '.txt')

if __name__ == "__main__":
    import pickle
    from identify_hot_topics import HotTopics
    import analyse_article_clusters
    ht = HotTopics()
    db = pickle.load(open(r'./data/db.p', 'rb'))
    clusters = pickle.load(open(r'./data/community_dendogram.p', 'rb'))
    articles = []
    ids = []
    from export_to_vos import prettify
    for a in db:
        articles.append(prettify(db[a]['title'] + db[a]['summary']))
        ids.append(a)
    clusters = cluster_texts(articles, 7)
    cclusters = pickle.load(open(r'./data/cluster_by_text.p', 'rb'))
    corpus_tokens = pickle.load(open(r'./data/total_text.p', 'rb'))
    corpus_common_terms = analyse_article_clusters.find_common_terms(corpus_tokens, 10000)

    for k in range(40):
        clst_text = [cobj['title'] + cobj['summary'] for cobj in [db[ids[sid]] for sid in clusters[k]]]
        cluster_words = []
        for txxxt in clst_text:
            cluster_words += ht.tokenize(txxxt)
        common_terms = analyse_article_clusters.find_common_terms(cluster_words, 1000)
        common_terms_norm = analyse_article_clusters.normalize_by_ref(common_terms, corpus_common_terms)
        tn = sorted(common_terms_norm, key=lambda x: common_terms_norm[x])
    # pprint(dict(clusters))
