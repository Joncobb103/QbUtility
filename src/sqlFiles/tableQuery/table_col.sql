SELECT column_name,data_type FROM information_schema.columns
where table_schema ='(REPLACE SCHEMA)'
and table_name = '(REPLACE TABLE)';