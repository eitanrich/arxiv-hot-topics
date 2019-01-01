from wordcloud import WordCloud

import pickle
from matplotlib import pyplot as plt

if __name__ == "__main__":
    db_file = r'./data/db.p'

    print('Loading...')
    db = pickle.load(open(db_file, 'rb'))

    year_step = 5
    for year in range(1990, 2019, year_step):
        print('Processing {}-{}...'.format(year, year+year_step-1))
        all_text = ' '.join([p['summary'] for p in db.values() if year <= int(p['published'].split('-')[0]) < year + year_step])
        print('Total text length =', len(all_text))

        wordcloud = WordCloud(max_font_size=60, width=600, height=300).generate(all_text)
        wordcloud.to_file('{}-{}.jpg'.format(year, year+year_step-1))

        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title('Years {} - {}'.format(year, year+year_step-1))
        plt.axis("off")
        plt.pause(0.1)
    plt.show()
