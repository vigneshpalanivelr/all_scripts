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


--FUNCTION	: To find view previlages for provided user
--USAGE		: SELECT * FROM view_privs('<user_name>');
--EXAMPLE	: SELECT * FROM view_privs('postgres');
CREATE OR REPLACE FUNCTION view_privs(text) RETURNS TABLE(username text, viewname regclass, PRIVILEGES text[]) AS
$$
SELECT  $1, c.oid::regclass, ARRAY(SELECT privs FROM UNNEST(ARRAY [
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'INSERT') THEN 'INSERT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'DELETE') THEN 'DELETE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRUNCATE') THEN 'TRUNCATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'REFERENCES') THEN 'REFERENCES' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRIGGER') THEN 'TRIGGER' ELSE NULL END)]) foo(privs) WHERE privs IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog','sys') 
	AND c.relkind='v' 
	AND has_table_privilege($1,c.oid,'SELECT, INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') 
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;


--FUNCTION	: To find sequence level previlages for provided user
--USAGE		: SELECT * FROM sequence_privs('<user_name>');
--EXAMPLE	: SELECT * FROM sequence_privs('postgres');
CREATE OR REPLACE FUNCTION sequence_privs(text) RETURNS TABLE(username text, SEQUENCE regclass, PRIVILEGES text[]) AS
$$
SELECT $1, c.oid::regclass, ARRAY(SELECT privs FROM UNNEST(ARRAY [
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END)]) foo(privs) WHERE privs IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog','sys') 
	AND c.relkind='S' 
	AND has_table_privilege($1,c.oid,'SELECT,UPDATE')  
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;


--FUNCTION	: To find all previlages for provided user
--USAGE		: SELECT * FROM all_privs('<user_name>');
--EXAMPLE	: SELECT * FROM all_privs('postgres');
CREATE OR REPLACE FUNCTION all_privs(text) RETURNS TABLE(username text, object_type text, OBJECT_NAME name, PRIVILEGES text[]) AS
$$
SELECT * FROM (
	SELECT username,'Database' AS object_type ,dbname::name AS OBJECT_NAME ,PRIVILEGES FROM database_privs($1)
	UNION ALL
	SELECT username,'Schema' AS object_type,schemaname::name AS OBJECT_NAME,PRIVILEGES FROM schema_privs($1)
	UNION ALL
	SELECT username,'Table' AS object_type ,relname::name AS OBJECT_NAME ,PRIVILEGES FROM table_privs($1)
	UNION ALL
	SELECT username,'View' AS object_type ,viewname::name AS OBJECT_NAME ,PRIVILEGES FROM view_privs($1)
	UNION ALL
	SELECT username,'View' AS object_type ,sequence::name AS OBJECT_NAME ,PRIVILEGES FROM sequence_privs($1)
	UNION ALL
	SELECT username,'View' AS object_type ,spcname::name AS OBJECT_NAME ,PRIVILEGES FROM tablespace_privs($1)
) AS user_previlages
ORDER BY object_type;
$$ LANGUAGE SQL;



