import os
import numpy as np
import pickle as pkl
from matplotlib import pyplot as plt
from collections import Counter

clusters = pkl.load(open(r'./data/clusters_id_list.p', 'rb'))
id_to_year = pkl.load(open(r'./data/all_ids_to_years.p', 'rb'))

header = """
<html>
<head>
<style>
div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 400px;
}

div.gallery:hover {
  border: 1px solid #777;
}

div.gallery img {
  width: 100%;
  height: auto;
}

div.desc {
  padding: 15px;
  text-align: center;
}
</style>
</head>
<body>
"""

footer = """
</div>

</body>
</html>
"""

with open('./output/list_clusters.html', 'w') as outf:
    print(header, file=outf)
    for i, c in enumerate(clusters):
        c_years = Counter([id_to_year[id] for id in c])
        recent_part = (c_years.get(2018, 0) + c_years.get(2017, 0)) / float(len(c))
        is_very_hot = len(c) > 100 and recent_part > 0.65
        is_hot = len(c) > 100 and recent_part > 0.5
        if is_very_hot:
              print('<div style="background-color:red" class="gallery">', file=outf)
        elif is_hot:
              print('<div style="background-color:blue" class="gallery">', file=outf)
        else:
            print('<div class="gallery">', file=outf)
        print('  <a target="_blank" href="clusters/{}/papers_list.txt">'.format(i), file=outf)
        print('    <img src="clusters/{}/wordcloud.jpg" alt="Forest" width="600" height="400">'.format(i), file=outf)
        print('  </a>', file=outf)
        print('  <div class="desc">Cluster {} - {} papers</div>'.format(i, len(c)), file=outf)
        print('</div>', file=outf)
        print('', file=outf)
    print(footer, file=outf)
