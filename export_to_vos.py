import networkx as nx
import pickle
import re
import nltk
# from nltk.corpus import stopwords
# stopwords.update(['assumption', 'article', 'study', 'propose', 'work', 'proposed', 'assume',
#                   'http', 'https', 'box', 'caption', 'instruction', 'figure', 'body', 'block', 'paragraph',
#                   'essay', 'write', 'explain', 'definition', 'notion', 'task', 'course', 'paper', 'chapter',
#                   'find', 'report', 'resaoning', 'reason', 'discover', 'opinion', 'popular', 'estimation',
#                   'reconstruction', 'theme', 'trend', 'book', 'method', 'item', 'report', 'explanation'])

gml_path = 'C:\\Users\Alacrity\Documents\\Uni\Data\project\pubmed_ML_couccor.net'
write_file_path = 'C:\\Users\Alacrity\Documents\\Uni\Data\project\db_dois.txt'

stops = ['assumption', 'article', 'study', 'propose', 'work', 'proposed', 'assume',
                  'http', 'https', 'box', 'caption', 'instruction', 'figure', 'body', 'block', 'paragraph',
                  'essay', 'write', 'explain', 'definition', 'notion', 'task', 'course', 'paper', 'chapter',
                  'find', 'report', 'resaoning', 'reason', 'discover', 'opinion', 'popular', 'estimation',
                    'overview', 'survey', 'review', 'approach', 'problem',
                  'reconstruction', 'theme', 'trend', 'book', 'method', 'item', 'report', 'explanation', 'answer']
def prettify(text):
    remove_chars = ["(", ")", "{", "}", "[", "]","*","$", "?", "\\", ":", "'", '"', ";", "`","-", "\n", "mathbf"]
    for char in remove_chars:
        text = text.replace(char, "")
    for word in stops:
        text = text.replace(" " + word + " ", "")
    text = text.replace('gpus', 'gpu')
    text = text.replace('car', 'vehicle')
    text  = text.replace('deep neural network', 'dnn')
    text  = text.replace('deep neural networks', 'dnn')
    text  = text.replace('adversary', 'adverserial')
    text  = text.replace('natural language processing', 'nlp')
    text = text.replace('convolutional neural networks', 'cnn')
    text = text.replace('convolutional neural network', 'cnn')
    text = text.lower()
    return text

def linefy(text, first):
    lines = []
    start_ch = "      "
    words = re.split('\n| ',text)
    curline = newline  = first
    for w in words:
        w.strip('\n')
        curline = newline
        if len(curline) + len(w) + 3 >= 89:
            curline += "\n"
            lines.append(curline)
            newline =  start_ch + w
        else:
            newline = curline + " " + w
    if lines and curline != lines[-1]:
        lines.append(curline + "\n")
    return lines

def write(db_path = r'./data/db.p', write_file_path = write_file_path):
    db = pickle.load(open(db_path, 'rb'))
    with open(write_file_path, 'w') as f:
        for item_id, metadata in db.items():
            year, month, day = metadata["published_parsed"].tm_year, metadata["published_parsed"].tm_mon, metadata["published_parsed"].tm_mday
            date = " ".join([str(year), str(month), str(day)])
            try:
                f.write("PMID- " + str(metadata['_rawid']) + "\n" + "OWN - NLM" + "\n" +
                        "STAT- Publisher" + "\n" + "LR  - 20190121" + "\n")
                f.write(("DP  - " + date + "\n"))
                f.writelines(linefy(prettify(metadata["title"]), "TI  -" ))
                f.writelines(linefy(prettify(metadata["summary"]), "AB  -" ))
                f.write("\n")
            except UnicodeEncodeError:
                continue
