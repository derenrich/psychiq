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
 ), title_texts AS (
   SELECT title,qid,page_id FROM `wikidata-319717.bq.enwiki_texts` join parsed_map ON title=UnescapeTitle(enwiki) 
 ), cats AS (
   SELECT page_id, category from `bq.enwiki_cats` where
     NOT (CONTAINS_SUBSTR(category, "Short description") OR CONTAINS_SUBSTR(category,"Articles with") OR CONTAINS_SUBSTR(category, "All stub articles") OR CONTAINS_SUBSTR(category, "Wikidata") OR CONTAINS_SUBSTR(category, "Noindexed pages") OR CONTAINS_SUBSTR(category, "Redirects") OR CONTAINS_SUBSTR(category, "All articles") OR CONTAINS_SUBSTR(category, " dates") OR CONTAINS_SUBSTR(category, "Wikipedia articles") OR CONTAINS_SUBSTR(category, "wayback links") OR CONTAINS_SUBSTR(category, "Pages containing") OR CONTAINS_SUBSTR(category, "Articles containing") OR CONTAINS_SUBSTR(category, "Articles using") OR CONTAINS_SUBSTR(category, "Articles needing"))
 ), cats_text AS (
   SELECT page_id, ARRAY_TO_STRING(ARRAY_AGG(category),"\n") as cat_text from cats group by page_id
 ) SELECT distinct COALESCE(relation_id,1001) as relation_id, CONCAT(cat_text,"\n",title) as text, qid from `bq.relation_ids` r right join parsed_targets t ON r.relation = t.relation and r.target=t.target inner join title_texts on qid=source join cats_text on cats_text.page_id = title_texts.page_id;
