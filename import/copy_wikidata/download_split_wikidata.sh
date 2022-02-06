#! /bin/bash
touch /tmp/boot0
apt update
apt -y install apache2
apt -y install python3-pip
apt -y install wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev cmake

gsutil cp  gs://wikidata-de/dump/wikidata-req/*py .
gsutil cp  gs://wikidata-de/dump/wikidata-req/requirements.txt .

pip3 install -r requirements.txt
echo "Running payload"
time python3 download_split_wikidata.py 2> /tmp/logerr | tee /tmp/log 
