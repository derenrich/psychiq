#! /bin/bash

REQ_FOLDER=wikidata-mapping-req

pip freeze > requirements.txt
gsutil cp *.py gs://wikidata-de/dump/$REQ_FOLDER/
gsutil cp requirements.txt gs://wikidata-de/dump/$REQ_FOLDER/requirements.txt

gcloud compute instances create wikidata-mapping-uploader \
  --zone us-west1-a \
  --boot-disk-size=250GB \
  --metadata-from-file=startup-script=download_wikidata_wiki_mapping.sh  \
  --scopes=storage-rw \
  --machine-type=n2-standard-2 \
  --image-project=ubuntu-os-cloud  --image-family=ubuntu-2004-lts

#gcloud compute instances delete wikidata-mapping-uploader