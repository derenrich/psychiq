import os
import sys
import bz2
import pandas as pd
import tqdm
import csv

DIR = "gs://wikidata-de/dump/wikidata-2022-11-04/"
URL = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.nt.bz2"
dump_idx = 0
BATCH_SIZE = 350000

def filter_link(link: str):
    if link.startswith("<http://www.wikidata.org/prop/direct/"):
        return True
    return False

def map_link(link: str):
    DIRECT_LINK = "<http://www.wikidata.org/prop/direct/"
    return link[len(DIRECT_LINK):-1]

def map_source(source:str):
    SOURCE_LINK = "<http://www.wikidata.org/entity/"
    return source[len(SOURCE_LINK):-1]

def dump_buff(buffer: list, local: bool):
    global dump_idx
    if buffer:
        df = pd.DataFrame.from_records(buffer, columns=['source', 'relation', 'target']).astype('string')
        fname = f"wikidata.{dump_idx}.parquet"
        df.to_parquet(fname)
        if not local:
            os.system(f"gsutil cp {fname} {DIR}{fname}")
            os.system(f"rm {fname}")
        dump_idx += 1

if __name__ == '__main__':
    print("Running Startup")
    local_run = 'LOCAL' in os.environ
    skip_download = 'SKIP' in os.environ
    if not skip_download:
        print("Downloading")
        os.system(f"wget '{URL.strip()}' -O dump.nt.bz2")
    print("Parsing...")
    with bz2.open("dump.nt.bz2", mode='rt', newline="") as f:
        buffer = []
        csv_reader = csv.reader(f, delimiter=' ', escapechar='\\')
        for t in tqdm.tqdm(csv_reader):
            t.pop()
            if filter_link(t[1]):
                t[0] = map_source(t[0])
                t[1] = map_link(t[1])
                buffer.append(t)
            if len(buffer) >= BATCH_SIZE:
                    print('index', dump_idx)
                    sys.stdout.flush()
                    dump_buff(buffer, local_run)
                    buffer = []
    dump_buff(buffer, local_run)
    print("@Startup Done@")
