import os
import gzip
import pandas as pd
import typing
import random

DIR = "gs://wikidata-de/dump/enwiki-cats-2022-11-10/"

dump_idx = 0
BATCH_SIZE = 500000

def parse(f: typing.BinaryIO):
    for l in f:
        if l.startswith(b"INSERT INTO `categorylinks` VALUES"):
            start_list = l.index(b'(')
            l = l[(start_list+1):]
            for tup in l.split(b'),('):
                page_id, rest = tup.split(b',',1)
                page_id = int(page_id)
                cat_name, rest = rest.split(b"','", 1)
                cat_name = cat_name[1:].decode('utf-8').replace("\\'", "'").replace("_", " ").replace('\\"', '"')
                yield (page_id, cat_name)

def dump_buff(buffer: list, local: bool):
    global dump_idx
    if buffer:
        random.shuffle(buffer)
        df = pd.DataFrame.from_records(buffer)
        fname = f"enwiki_cats.{dump_idx}.parquet"
        df.to_parquet(fname)
        if not local:
            os.system(f"gsutil cp {fname} {DIR}{fname}")
            os.system(f"rm {fname}")
        dump_idx += 1


if __name__ == '__main__':
    local_run = 'LOCAL' in os.environ
    skip_download = 'SKIP' in os.environ
    print("Running Startup")
    buffer = []
    if not skip_download:
        print("Downloading...")
        os.system(f"wget 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz' -O dump.sql.gz")
    print("Parsing...")
    with gzip.open('dump.sql.gz',mode='r') as f:
        for t in parse(f):
            page_id, category = t
            r = {}
            r['page_id'] = page_id
            r['category'] = category
            buffer.append(r)
            if len(buffer) > BATCH_SIZE:
                dump_buff(buffer, local_run)
                buffer = []
    dump_buff(buffer, local_run)
    print("@Startup Done@")
