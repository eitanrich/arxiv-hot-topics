from collections import Counter
import pickle
import nltk
import csv
import re
import matplotlib.pyplot as plt
import math
import os
import json

'''
def load_data():
    db_file = r'./data/db.p'
    db = pickle.load(open(db_file, 'rb'))
    return db
'''
class HotTopics(object):
    def __init__(self):
        nltk.download("stopwords")
        from nltk.corpus import stopwords
        self.english_stop_words = set(stopwords.words('english'))

    def tokenize(self, text):
        remove_chars = [".", ",", "(", ")", "{", "}", "[", "]", "$", "?", "\\", ":", "'", '"', ";", "`", "mathbf"]
        for char in remove_chars:
            text = text.replace(char, "")
        text = text.lower()
        tokens = text.split()
        tokens = [token for token in tokens if token not in self.english_stop_words]
        tokens = [token for token in tokens if not token.isnumeric()]
        return tokens


    def extract_yearly_texts(self):
        db = pickle.load(open(r'./data/db.p', 'rb'))
        print(len(db.items()))
        #exit()
        yearly_text = {}
        total_text = []
        idf_dict = Counter()
        N = 0
        for item_id, metadata in db.items():
            if N % 1000 == 0:
                print(N)
            N += 1
            year = int(metadata["published"][:4])
            categories = [category["term"] for category in metadata["tags"]]
            text = metadata["title"] + " " + metadata["summary"]
            tokens = self.tokenize(text)
            total_text += tokens
            for category in categories:
                if category not in yearly_text:
                    yearly_text[category] = {}
                    #idf_dict[category] = {}
                if year not in yearly_text[category]:
                    yearly_text[category][year] = []
                    #idf_dict[category][year] = []
                yearly_text[category][year] += tokens
            idf_dict += Counter(set(tokens))
        idf_dict = {a:math.log(N/b) for (a,b) in idf_dict.items()}
        pickle.dump(yearly_text, open("./data/yearly_text.p","wb"))
        pickle.dump(total_text, open("./data/total_text.p","wb"))
        pickle.dump(idf_dict, open("./data/idf_dict.p","wb"))
        return yearly_text, total_text

def get_bigrams(text):
    bigrams = [" ".join(bigram) for bigram in zip(*[text, text[1:]])]
    return bigrams


def get_trigrams(text):
    trigrams = [" ".join(trigram) for trigram in zip(text, text[1:], text[2:])]
    return trigrams

def normalize_counter(ctr):
    total = sum(ctr.values())
    for key in ctr:
        ctr[key] /= total


def most_common():
    total_text = pickle.load(open(r'./data/total_text.p', 'rb'))
    ctr = Counter(total_text)
    print(ctr.most_common(100))
    bigrams = get_bigrams(total_text)
    bigram_ctr = Counter(bigrams)
    print(bigram_ctr.most_common(100))

def top_increase(curr_counter, past_counter):
    past_counter = {a:b for a,b in past_counter.items() if b>5}
    curr_counter = {a:b for a,b in curr_counter.items() if b>5}
    normalize_counter(past_counter)
    normalize_counter(curr_counter)
    ratio_ctr = Counter()
    new_comers = Counter()
    for key in set(past_counter.keys()) | set(curr_counter.keys()):
        if key not in curr_counter:
            continue #downward trend
        elif key not in past_counter:
            new_comers[key] = curr_counter[key]
        else:
            ratio_ctr[key] = curr_counter[key] / past_counter[key]
    return ratio_ctr, new_comers

def hottest(category, curr_year):
    #ht = HotTopics()
    #ht.extract_yearly_texts()
    yearly_text = pickle.load(open(r'./data/yearly_text.p', 'rb'))
    curr_text = yearly_text[category][curr_year]
    prev_period = range(curr_year-5, curr_year)
    past_text = []
    for past_year in prev_period:
        past_text += yearly_text[category][past_year]
    #exit()
    past_counter = Counter(past_text)
    curr_counter = Counter(curr_text)
    ratio_ctr, new_comers = top_increase(curr_counter, past_counter)
    top_unigram = ratio_ctr.most_common(100)
    new_comers_unigram = new_comers.most_common(100)
    least_unigram = ratio_ctr.most_common()[:-100-1:-1]

    past_bigrams = get_bigrams(past_text)
    curr_bigrams = get_bigrams(curr_text)
    #print(past_bigrams)
    past_counter = Counter(past_bigrams)
    curr_counter = Counter(curr_bigrams)
    #exit()
    ratio_ctr, new_comers = top_increase(curr_counter, past_counter)
    top_bigram = ratio_ctr.most_common(100)
    new_comers_bigram = new_comers.most_common(100)
    least_bigram = ratio_ctr.most_common()[:-100-1:-1]

    past_trigrams = get_trigrams(past_text)
    curr_trigrams = get_trigrams(curr_text)
    #print(past_bigrams)
    past_counter = Counter(past_trigrams)
    curr_counter = Counter(curr_trigrams)
    #exit()
    ratio_ctr, new_comers = top_increase(curr_counter, past_counter)
    top_trigram = ratio_ctr.most_common(100)
    new_comers_trigram = new_comers.most_common(100)
    least_trigram = ratio_ctr.most_common()[:-100-1:-1]

    return top_unigram, new_comers_unigram, least_unigram, top_bigram, new_comers_bigram, least_bigram, top_trigram, new_comers_trigram, least_trigram


def write_to_file(filename, line):
    with open("output/"+filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(line)

def output_yearly_results():
    filenames = ["top_unigram", "new_comers_unigram", "least_unigram", "top_bigram", "new_comers_bigram", "least_bigram", "top_trigram", "new_comers_trigram", "least_trigram"]
    #for filename in filenames:
    #    write_to_file(filename, list(range(11)))
    categories = ['cs.CV', 'cs.AI', 'cs.LG', 'cs.CL', 'cs.NE', 'stat.ML']
    output = {}
    for year in range(2012,2019):
        for category in categories:
            #print("year", year)
            hottest_results = hottest(category, year)
            for (curr_filename, curr_results) in zip(filenames, hottest_results):
                if year not in output:
                    output[year] = {}
                if category not in output[year]:
                    output[year][category] = {}
                output[year][category][curr_filename] = [item for item in curr_results[:10]]
                #line = [year] + [item for item in curr_results[:10]]
                #write_to_file(curr_filename, line)
    js_out = json.dumps(output)
    print(js_out)
    exit()


def test():
    pass
    exit()

def draw(x, y, xlabel, ylabel, title, label):
    plt.plot(x,y,label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc='upper left')
    #plt.savefig("output/"+title+".png")
    plt.savefig("output/term_popularity.png")
    #plt.close()


def normalize_yearly_counters():
    yearly_text = pickle.load(open(r'./data/yearly_text.p', 'rb'))
    normalized_yearly_counters = {}
    for category in yearly_text:
        normalized_yearly_counters[category] = {}
        for year in yearly_text[category]:
            ctr = Counter(yearly_text[category][year])
            normalize_counter(ctr)
            normalized_yearly_counters[category][year] = ctr
    pickle.dump(normalized_yearly_counters, open("./data/normalized_yearly_counters.p", "wb"))



def graph_text(text, category, draw = True):
    yearly_text = pickle.load(open(r'./data/normalized_yearly_counters.p', 'rb'))
    years = sorted(yearly_text[category])
    yearly_values = [yearly_text[category][year][text] for year in years]
    if draw:
        draw(years, yearly_values, "years", "occurrences", "Occurrences by year in " + category, text)
    else:
        filename = category + "_" + text + ".csv"
        output = zip(years, yearly_values)
        write_to_file(filename, ["year", "popularity"])
        for line in output:
            write_to_file(filename, line)
"""
def tf(year):
    tf_dict = {}
    #for prefix in prefixes:
    #    tf_dict[prefix] = Counter()
    #    print(prefix)
    for category in yearly_text:
        tf_dict[category] = {}
        for year in yearly_text[category]
        #if category.startswith(prefix):
        print(category)
        cat_dict = sum((Counter(year) for year in yearly_text[category].values()), Counter())
        print(cat_dict.most_common(50))
        tf_dict[prefix] += cat_dict
    print(tf_dict[prefix].most_common(100))
    tf_dict[prefix] = {entry:math.log(tf_dict[prefix][entry] + 1) for entry in tf_dict}
    return tf_dict
"""

def tf_idf():
    tf_idf_filename = "./data/tf_idf_dict.p"
    if os.path.exists(tf_idf_filename):
        return pickle.load(open(tf_idf_filename, 'rb'))

    yearly_text = pickle.load(open(r'./data/yearly_text.p', 'rb'))
    idf_dict = pickle.load(open(r'./data/idf_dict.p', 'rb'))
    #prefixes = ["cs.", "math.", "physics.", "stat.", "astro-ph.", "q-bio.", "cond-mat.", "hep-"]
    tf_idf_dict = {}
    categories = ['cs.CV', 'cs.AI', 'cs.LG', 'cs.CL', 'cs.NE', 'stat.ML']
    for category in categories:
        tf_idf_dict[category] = {}
        for year in yearly_text[category]:
            tf = Counter(yearly_text[category][year])
            #print(tf.most_common(100))
            tf_idf_dict[category][year] = Counter({token:math.log(tf[token]+1) * idf_dict[token] for token in tf if tf[token] > 10})
    pickle.dump(tf_idf_dict, open(tf_idf_filename,"wb"))
    return tf_idf_dict
    #exit()

import os


def pickle_to_json():
    yearly_text = pickle.load(open(r'./data/normalized_yearly_counters.p', 'rb'))
    tokens = {}
    for cat in yearly_text:
        for year in yearly_text[cat]:
            for token in yearly_text[cat][year]:
                key = cat+"_"+token
                if key not in tokens:
                    tokens[key] = {}
                tokens[key][year] = yearly_text[cat][year][token]
    json.dump(tokens, open("data/word_counts.json", "w",encoding="utf-8"))
    exit()
    """
    for token in tokens:
        try:
            path = "data/ngrams_data/"+token+".json"
            dir_name = os.path.dirname(os.path.abspath(path))
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            json.dump(tokens[token], open(path, "w",encoding="utf-8"))
        except:
            pass
        #exit()
    
    #json.dump(yearly_text,open(r'./data/normalized_yearly_counters.json', 'w', encoding="utf8"))
    exit()
    """


def trim_word_counts():
    word_counts = json.load(open("data/word_counts.json", "r",encoding="utf-8"))
    full = json.dumps(word_counts)

    print(sum(word_counts["stat.ml_svm"].values()))
    print(sum(word_counts["stat.ml_cnn"].values()))
    print(sum(word_counts["stat.ml_boosting"].values()))
    #exit()
    thresh = 0.001
    categories = [cat.lower() for cat in ['cs.CV', 'cs.AI', 'cs.LG', 'cs.CL', 'cs.NE', 'stat.ML']]
    word_counts = {a:list(sorted(b.items())) for (a,b) in word_counts.items() if any(a.startswith(cat) for cat in categories) and " " not in a and sum(b.values()) > thresh}
    json.dump(word_counts, open("data/trim_word_counts.json", "w",encoding="utf-8"))
    json_string = json.dumps(word_counts)
    with open("html/test/ngrams.html", "r") as f:
        text = f.read()
        text = text.replace("var data_json = replace", "var data_json = '" + json_string + "'")
        with open("html/test/ngrams2.html", "w") as f:
            f.write(text)

    with open("html/test/ngrams.html", "r") as f:
        text = f.read()
        text = text.replace("var data_json = replace", "var data_json = '" + full + "'")
        with open("html/test/ngrams_full.html", "w") as f:
            f.write(text)

    #print(word_counts)
    exit()


if __name__ == "__main__":

    trim_word_counts()

    output_yearly_results()


    """
    tokens = json.load(open("data/word_counts.json", "r",encoding="utf-8"))
    tokens = {a.lower():b for (a,b) in tokens.items()}
    json.dump(tokens, open("data/word_counts.json", "w",encoding="utf-8"))
    """

    exit()
    pickle_to_json()
    graph_text("cnn", "cs.NE", False)

    #tf_idf_dict = tf_idf()
    #for cat in sorted(tf_idf_dict):
    #    for year in sorted(tf_idf_dict[cat]):
    #        print(cat, year, tf_idf_dict[cat][year].most_common(20))

    #ht = HotTopics()
    #ht.extract_yearly_texts()
    #exit()
    #output_yearly_results()
    #search_items = ["cnn", "gan", "lstm", "mle", "hmm", "adaboost"]
    #for search_item in search_items:
    #    graph_text(search_item, "stat.ML")


