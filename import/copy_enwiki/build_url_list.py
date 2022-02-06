# generates a file that lists all the URLs for the split enwiki page XML dump
# for use in dataflow jobs

import requests
import re
import os
def get_url_list():
    ROOT = "https://dumps.wikimedia.org/enwiki/latest/"
    res = requests.get(ROOT)
    found = re.findall(r"enwiki-latest-pages-articles-multistream\d+\.xml-p\d+p\d+.bz2", res.content.decode('utf-8'))


    with open('urls.csv', 'w') as f:
        for p in set(found):
            f.write(ROOT + p + "\n")


if __name__ == '__main__':
    get_url_list()
    os.system("gsutil cp urls.csv gs://wikidata-de/dump/urls.csv")