import os
import mwxml
import mwtypes
import bz2
import tqdm
import pandas as pd
from build_url_list import get_url_list


DIR = "gs://wikidata-de/dump/enwiki-2002-02-05/"

dump_idx = 0
BATCH_SIZE = 10000

def process(page: mwtypes.Page, rev: mwtypes.Revision):
    pg = {}
    if page.namespace == 0:
        pg['title'] = page.title
        pg['page_id'] = page.id
        pg['redirect'] = page.redirect
        pg['text'] = rev.text        
        return pg

def dump_buff(buffer: list, local: bool):
    global dump_idx
    if buffer:
        df = pd.DataFrame.from_records(buffer)
        fname = f"enwiki.{dump_idx}.parquet"
        df.to_parquet(fname)
        if not local:
            os.system(f"gsutil cp {fname} {DIR}{fname}")
            os.system(f"rm {fname}")
        dump_idx += 1


if __name__ == '__main__':
    local_run = 'LOCAL' in os.environ
    skip_download = 'SKIP' in os.environ
    print("Running Startup")
    get_url_list()
    with open('urls.csv') as f:
        buffer = []
        for url in f.readlines():
            if not skip_download:
                print("Downloading...")
                os.system(f"wget '{url.strip()}' -O dump.xml.bz2")
            print("Parsing...")
            dump = mwxml.Dump.from_file(bz2.open("dump.xml.bz2"))        
            for page in tqdm.tqdm(dump):
                for revision in page:
                    res = process(page, revision)
                    if res:
                        buffer.append(res)
                if len(buffer) >= BATCH_SIZE:
                    dump_buff(buffer, local_run)
                    buffer = []
        dump_buff(buffer)
    print("@Startup Done@")
