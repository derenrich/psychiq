import os
import sys
import bz2
import pandas as pd
import traceback
import tqdm
import csv

DIR = "gs://wikidata-de/dump/wikidata-wikipedia-mapping-2022-11-04/"
URL = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.nt.bz2"
dump_idx = 0
BATCH_SIZE = 80000

def filter_link(link: str):
    return link == "<http://schema.org/about>"

def filter_source(source:str):
    return source.startswith("<https://en.wikipedia.org/wiki/")    

def map_target(target: str):
    ENT_LINK = "<http://www.wikidata.org/entity/"
    if target.startswith(ENT_LINK):
        return target[len(ENT_LINK):-1]
    return target

def map_source(source: str):
    WIKI_LINK = "<https://en.wikipedia.org/wiki/"
    if source.startswith(WIKI_LINK):
        return source[len(WIKI_LINK):-1]
    return source

def dump_buff(buffer: list, local: bool):
    global dump_idx
    if buffer:
        df = pd.DataFrame.from_records(buffer, columns=['enwiki', 'qid']).astype('string')
        fname = f"wikidata-mapping.{dump_idx}.parquet"
        df.to_parquet(fname)
        if not local:
            os.system(f"gsutil cp {fname} {DIR}{fname}")
            os.system(f"rm {fname}")
        dump_idx += 1


if __name__ == "__main__":
    print("Running Startup")
    local_run = 'LOCAL' in os.environ
    skip_download = 'SKIP' in os.environ
    if not skip_download:
        os.system(f"wget '{URL.strip()}' -O dump.nt.bz2")
    with bz2.open("dump.nt.bz2", mode='rt', newline="") as f:
        csv_reader = csv.reader(f, delimiter=' ', escapechar='\\')
        buffer = []
        for t in tqdm.tqdm(csv_reader):
            t.pop()
            if len(t) != 3:
                continue
            if filter_link(t[1]) and filter_source(t[0]):
                t[2] = map_target(t[2])
                t[0] = map_source(t[0])
                buffer.append((t[0], t[2]))
            if len(buffer) >= BATCH_SIZE:
                print('index', dump_idx)
                sys.stdout.flush()
                dump_buff(buffer, local_run)
                buffer = []
        dump_buff(buffer, local_run)
    print("@Startup Done@")
