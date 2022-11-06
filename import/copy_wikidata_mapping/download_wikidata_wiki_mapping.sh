#! /bin/bash
REQ_FOLDER=wikidata-mapping-req

apt update
apt -y install apache2
apt -y install python3-pip
apt -y install wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev cmake

gsutil cp  gs://wikidata-de/dump/$REQ_FOLDER/*py .
gsutil cp  gs://wikidata-de/dump/$REQ_FOLDER/requirements.txt .

pip3 install -r requirements.txt
echo "Starting..."
time python3  download_wikidata_wiki_mapping.py 2> /tmp/logerr | tee /tmp/log 
echo "Done!"