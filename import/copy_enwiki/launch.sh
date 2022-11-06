#! /bin/bash

pip freeze > requirements.txt
gsutil cp *.py gs://wikidata-de/dump/enwiki-reqs/
gsutil cp requirements.txt gs://wikidata-de/dump/enwiki-reqs/requirements.txt

gcloud compute instances create enwiki-uploader \
  --zone us-west1-a \
  --boot-disk-size=200GB \
  --metadata-from-file=startup-script=download_split_enwiki.sh  \
  --scopes=storage-rw \
  --machine-type=n2-standard-2 \
  --image-project=ubuntu-os-cloud  --image-family=ubuntu-2004-lts

#gcloud compute instances delete enwiki-uploader
