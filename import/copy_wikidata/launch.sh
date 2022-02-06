#! /bin/bash

pip freeze > requirements.txt
gsutil cp *.py gs://wikidata-de/dump/wikidata-req/
gsutil cp requirements.txt gs://wikidata-de/dump/wikidata-req/requirements.txt

gcloud compute instances create wikidata-uploader \
  --zone us-west1-a \
  --boot-disk-size=250GB \
  --metadata-from-file=startup-script=download_split_wikidata.sh  \
  --scopes=storage-rw \
  --machine-type=n2-standard-2 \
  --image-project=ubuntu-os-cloud  --image-family=ubuntu-2004-lts