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



