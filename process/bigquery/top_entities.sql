CREATE TEMP FUNCTION ParseEntity(uri string) RETURNS string AS (
  REGEXP_EXTRACT(uri, "<http://www.wikidata.org/entity/(Q\\d+)>")
);

#hack
CREATE TEMP FUNCTION UnescapeTitle(title string) RETURNS string AS (
  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(title, "_", " "), "%26", "&"),"%27","'"), "%C3%A9", "é"),"%3F","?"), "%E2%80%93", "–"),"%22","\""),"%C3%AD","í")
);


WITH parsed_targets AS 
 (
   SELECT source, relation, ParseEntity(target) as target
   FROM `wikidata-319717.bq.wd_statements`
   WHERE relation='P31' or relation="P279"
 ),
  parsed_map AS (
   SELECT qid, enwiki FROM `wikidata-319717.bq.wd_map`
   WHERE REGEXP_EXTRACT(enwiki, "^([^:]+):?") NOT IN ("Category", "Template", "Wikipedia", "Portal", "Module", "Help", "User")
 ), texts AS (
   SELECT text,qid FROM `wikidata-319717.bq.enwiki_texts` join parsed_map ON title=UnescapeTitle(enwiki) 
 ), top_qids as (
   SELECT target, relation, count(*) as count  FROM parsed_targets join texts ON qid=source  group by target, relation order by count(*) desc LIMIT 1000
 ) SELECT *, ROW_NUMBER() OVER (ORDER BY count DESC) as relation_id from top_qids
