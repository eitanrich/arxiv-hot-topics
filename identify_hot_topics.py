from collections import Counter
import pickle
import nltk
import csv
import re
import matplotlib.pyplot as plt


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
        yearly_text = {}
        total_text = []
        for item_id, metadata in db.items():
            year = int(metadata["published"][:4])
            categories = [category["term"] for category in metadata["tags"]]
            text = metadata["title"] + " " + metadata["summary"]
            tokens = self.tokenize(text)
            total_text += tokens
            for category in categories:
                if category not in yearly_text:
                    yearly_text[category] = {}
                if year not in yearly_text[category]:
                    yearly_text[category][year] = []
                yearly_text[category][year] += tokens
        pickle.dump(yearly_text, open("./data/yearly_text.p","wb"))
        pickle.dump(total_text, open("./data/total_text.p","wb"))
        return yearly_text, total_text

def get_bigrams(text):
    bigrams = [" ".join(bigram) for bigram in zip(*[text, text[1:]])]
    return bigrams


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
    return top_unigram, new_comers_unigram, least_unigram, top_bigram, new_comers_bigram, least_bigram


def write_to_file(filename, line):
    with open("output/"+filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(line)

def output_yearly_results():
    filenames = ["top_unigram.csv", "new_comers_unigram.csv", "least_unigram.csv", "top_bigram.csv", "new_comers_bigram.csv", "least_bigram.csv"]
    for filename in filenames:
        write_to_file(filename, list(range(11)))
    for year in list(range(2012,2019))[::-1]:
        print("year", year)
        hottest_results = hottest("stat.ML", year)
        for (curr_filename, curr_results) in zip(*[filenames, hottest_results]):
            line = [year] + [item for item in curr_results[:10]]
            write_to_file(curr_filename, line)



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



def graph_text(text, category):
    yearly_text = pickle.load(open(r'./data/normalized_yearly_counters.p', 'rb'))
    yearly_values = [yearly_text[category][year][text] for year in sorted(yearly_text[category])]
    years = sorted(yearly_text[category])
    print(yearly_values)
    print(years)
    draw(years, yearly_values, "years", "occurrences", "Occurrences by year in " + category, text)

if __name__ == "__main__":
    #output_yearly_results()
    search_items = ["cnn", "gan", "lstm", "mle", "hmm", "adaboost"]
    for search_item in search_items:
        graph_text(search_item, "stat.ML")


