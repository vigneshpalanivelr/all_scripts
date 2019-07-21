--VIEW		: To list all functions created on a DB
--USAGE		: SELECT * FROM show_functions;
--USAGE		: DROP FUNCTION IF EXISTS <function_name> CASCADE;
CREATE OR REPLACE VIEW show_functions AS
	SELECT routine_name 
	FROM information_schema.routines 
	WHERE routine_type='FUNCTION' 
		AND specific_schema NOT IN ('pg_catalog','information_schema');


--FUNCTION	: To find database level previlages for provided user
--USAGE		: SELECT * FROM database_privs('<user_name>');
--EXAMPLE	: SELECT * FROM database_privs('postgres');
CREATE OR REPLACE FUNCTION database_privs(text) RETURNS TABLE(username text,dbname name,PRIVILEGES  text[]) AS
$$
SELECT $1, datname, ARRAY(SELECT privs FROM UNNEST(ARRAY[
	(CASE WHEN has_database_privilege($1,c.oid,'CONNECT') THEN 'CONNECT' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'CREATE') THEN 'CREATE' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'TEMPORARY') THEN 'TEMPORARY' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'TEMP') THEN 'CONNECT' ELSE NULL END)])foo(privs) WHERE privs IS NOT NULL) 
FROM pg_database c 
WHERE  has_database_privilege($1,c.oid,'CONNECT,CREATE,TEMPORARY,TEMP') 
	AND datname NOT IN ('template0','template1');
$$ LANGUAGE SQL;


--FUNCTION	: To find schema level previlages for provided user
--USAGE		: SELECT * FROM schema_privs('<user_name>');
--EXAMPLE	: SELECT * FROM schema_privs('postgres');
CREATE OR REPLACE FUNCTION schema_privs(text) RETURNS TABLE(username text, schemaname name, PRIVILEGES text[]) AS
$$
SELECT $1, c.nspname, ARRAY(SELECT privs FROM UNNEST(ARRAY[
	(CASE WHEN has_schema_privilege($1,c.oid,'CREATE') THEN 'CREATE' ELSE NULL END),
	(CASE WHEN has_schema_privilege($1,c.oid,'USAGE') THEN 'USAGE' ELSE NULL END)])foo(privs) WHERE privs IS NOT NULL)
FROM pg_namespace c 
WHERE c.nspname NOT IN ('information_schema','pg_catalog')
	AND has_schema_privilege($1,c.oid,'CREATE,USAGE');
$$ LANGUAGE SQL;


--FUNCTION	: To find table level previlages for provided user
--USAGE		: SELECT * FROM table_privs('<user_name>');
--EXAMPLE	: SELECT * FROM table_privs('postgres');
CREATE OR REPLACE FUNCTION table_privs(text) RETURNS TABLE(username text, relname regclass, PRIVILEGES text[]) AS
$$
SELECT $1,c.oid::regclass, ARRAY(SELECT privs FROM UNNEST(ARRAY [ 
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'INSERT') THEN 'INSERT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'DELETE') THEN 'DELETE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRUNCATE') THEN 'TRUNCATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'REFERENCES') THEN 'REFERENCES' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRIGGER') THEN 'TRIGGER' ELSE NULL END)]) foo(privs) WHERE privs IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog')  
	AND c.relkind='r' 
	AND has_table_privilege($1,c.oid,'SELECT, INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') 
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;


--FUNCTION	: To find tablespace level previlages for provided user
--USAGE		: SELECT * FROM tablespace_privs('<user_name>');
--EXAMPLE	: SELECT * FROM tablespace_privs('postgres');
CREATE OR REPLACE FUNCTION tablespace_privs(text) RETURNS TABLE(username text,spcname name,PRIVILEGES text[]) AS
$$
SELECT $1, spcname, ARRAY[
	(CASE WHEN has_tablespace_privilege($1,spcname,'CREATE') THEN 'CREATE' ELSE NULL END)] 
FROM pg_tablespace 
WHERE has_tablespace_privilege($1,spcname,'CREATE');
$$ LANGUAGE SQL;



