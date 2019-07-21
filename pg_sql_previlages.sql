--VIEW		: To list all functions created on a DB
--USAGE		: SELECT * FROM show_functions;
--USAGE		: DROP FUNCTION IF EXISTS <function_name> CASCADE;
CREATE OR REPLACE VIEW show_functions AS
	SELECT routine_name 
	FROM information_schema.routines 
	WHERE routine_type='FUNCTION' 
		AND specific_schema NOT IN ('pg_catalog','information_schema');
ALTER TABLE public.show_functions OWNER TO <username>;


--FUNCTION	: To find database level previlages for provided user
--USAGE		: SELECT * FROM database_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM database_privileges('postgres');
CREATE TYPE database_privileges_type AS (username text,dbname name,PRIVILEGES  text[]);
CREATE OR REPLACE FUNCTION database_privileges(text) RETURNS SETOF database_privileges_type AS
$$
SELECT $1, datname, ARRAY(SELECT privileges FROM UNNEST(ARRAY[
	(CASE WHEN has_database_privilege($1,c.oid,'CONNECT') THEN 'CONNECT' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'CREATE') THEN 'CREATE' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'TEMPORARY') THEN 'TEMPORARY' ELSE NULL END),
	(CASE WHEN has_database_privilege($1,c.oid,'TEMP') THEN 'CONNECT' ELSE NULL END)])foo(privileges) WHERE privileges IS NOT NULL) 
FROM pg_database c 
WHERE  has_database_privilege($1,c.oid,'CONNECT,CREATE,TEMPORARY,TEMP') 
	AND datname NOT IN ('template0','template1');
$$ LANGUAGE SQL;
ALTER FUNCTION database_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION database_privileges(text) IS 'This will list all the database previlages for a user';


--FUNCTION	: To find schema level previlages for provided user
--USAGE		: SELECT * FROM schema_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM schema_privileges('postgres');
CREATE TYPE schema_privileges_type AS (username text, schemaname name, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION schema_privileges(text) RETURNS SETOF schema_privileges_type AS
$$
SELECT $1, c.nspname, ARRAY(SELECT privileges FROM UNNEST(ARRAY[
	(CASE WHEN has_schema_privilege($1,c.oid,'CREATE') THEN 'CREATE' ELSE NULL END),
	(CASE WHEN has_schema_privilege($1,c.oid,'USAGE') THEN 'USAGE' ELSE NULL END)])foo(privileges) WHERE privileges IS NOT NULL)
FROM pg_namespace c 
WHERE c.nspname NOT IN ('information_schema','pg_catalog')
	AND has_schema_privilege($1,c.oid,'CREATE,USAGE');
$$ LANGUAGE SQL;
ALTER FUNCTION schema_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION schema_privileges(text) IS 'This will list all the schema privileges for a user';


--FUNCTION	: To find table level previlages for provided user
--USAGE		: SELECT * FROM table_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM table_privileges('postgres');
CREATE TYPE table_privileges_type AS (username text, relname regclass, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION table_privileges(text) RETURNS SETOF table_privileges_type AS
$$
SELECT $1,c.oid::regclass, ARRAY(SELECT privileges FROM UNNEST(ARRAY [ 
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'INSERT') THEN 'INSERT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'DELETE') THEN 'DELETE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRUNCATE') THEN 'TRUNCATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'REFERENCES') THEN 'REFERENCES' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRIGGER') THEN 'TRIGGER' ELSE NULL END)]) foo(privileges) WHERE privileges IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog')  
	AND c.relkind='r' 
	AND has_table_privilege($1,c.oid,'SELECT, INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') 
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;
ALTER FUNCTION table_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION table_privileges(text) IS 'This will list all the table privileges for a user';


--FUNCTION	: To find tablespace level previlages for provided user
--USAGE		: SELECT * FROM tablespace_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM tablespace_privileges('postgres');
CREATE TYPE tablespace_privileges_type AS (username text,spcname name,PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION tablespace_privileges(text) RETURNS SETOF tablespace_privileges_type AS
$$
SELECT $1, spcname, ARRAY[
	(CASE WHEN has_tablespace_privilege($1,spcname,'CREATE') THEN 'CREATE' ELSE NULL END)] 
FROM pg_tablespace 
WHERE has_tablespace_privilege($1,spcname,'CREATE');
$$ LANGUAGE SQL;
ALTER FUNCTION tablespace_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION tablespace_privileges(text) IS 'This will list all the tablespace privileges for a user';


--FUNCTION	: To find view previlages for provided user
--USAGE		: SELECT * FROM view_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM view_privileges('postgres');
CREATE TYPE view_privileges_type AS (username text, viewname regclass, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION view_privileges(text) RETURNS SETOF view_privileges_type AS
$$
SELECT  $1, c.oid::regclass, ARRAY(SELECT privileges FROM UNNEST(ARRAY [
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'INSERT') THEN 'INSERT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'DELETE') THEN 'DELETE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRUNCATE') THEN 'TRUNCATE' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'REFERENCES') THEN 'REFERENCES' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'TRIGGER') THEN 'TRIGGER' ELSE NULL END)]) foo(privileges) WHERE privileges IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog','sys') 
	AND c.relkind='v' 
	AND has_table_privilege($1,c.oid,'SELECT, INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') 
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;
ALTER FUNCTION view_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION view_privileges(text) IS 'This will list all the view privileges for a user';


--FUNCTION	: To find sequence level previlages for provided user
--USAGE		: SELECT * FROM sequence_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM sequence_privileges('postgres');
CREATE TYPE sequence_privileges_type AS (username text, SEQUENCE regclass, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION sequence_privileges(text) RETURNS SETOF sequence_privileges_type AS
$$
SELECT $1, c.oid::regclass, ARRAY(SELECT privileges FROM UNNEST(ARRAY [
	(CASE WHEN has_table_privilege($1,c.oid,'SELECT') THEN 'SELECT' ELSE NULL END),
	(CASE WHEN has_table_privilege($1,c.oid,'UPDATE') THEN 'UPDATE' ELSE NULL END)]) foo(privileges) WHERE privileges IS NOT NULL) 
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid 
WHERE n.nspname NOT IN ('information_schema','pg_catalog','sys') 
	AND c.relkind='S' 
	AND has_table_privilege($1,c.oid,'SELECT,UPDATE')  
	AND has_schema_privilege($1,c.relnamespace,'USAGE')
$$ LANGUAGE SQL;
ALTER FUNCTION sequence_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION sequence_privileges(text) IS 'This will list all the sequence privileges for a user';


--FUNCTION	: To find all previlages for provided user
--USAGE		: SELECT * FROM all_privileges('<user_name>');
--EXAMPLE	: SELECT * FROM all_privileges('postgres');
CREATE TYPE all_privileges_type AS (username text, object_type text, OBJECT_NAME name, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION all_privileges(text) RETURNS SETOF all_privileges_type AS
$$
SELECT * FROM (
	SELECT username,'Database' AS object_type ,dbname::name AS OBJECT_NAME ,PRIVILEGES FROM database_privileges($1)
	UNION ALL
	SELECT username,'Schema' AS object_type,schemaname::name AS OBJECT_NAME,PRIVILEGES FROM schema_privileges($1)
	UNION ALL
	SELECT username,'Table' AS object_type ,relname::name AS OBJECT_NAME ,PRIVILEGES FROM table_privileges($1)
	UNION ALL
	SELECT username,'View' AS object_type ,viewname::name AS OBJECT_NAME ,PRIVILEGES FROM view_privileges($1)
	UNION ALL
	SELECT username,'Sequence' AS object_type ,sequence::name AS OBJECT_NAME ,PRIVILEGES FROM sequence_privileges($1)
	UNION ALL
	SELECT username,'Tablespace' AS object_type ,spcname::name AS OBJECT_NAME ,PRIVILEGES FROM tablespace_privileges($1)
) AS user_previlages
ORDER BY object_type;
$$ LANGUAGE SQL;
ALTER FUNCTION all_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION all_privileges(text) IS 'This will list all privileges for a user (Database | Schema | Table | View | Sequence | Tablespace)';


--FUNCTION	: To find ALL previlages for ALL Users
--USAGE		: SELECT * FROM all_user_privileges();
--If Req    : CREATE TYPE all_user_privileges_type AS (username text, object_type text,object_name name, PRIVILEGES text[]);
CREATE OR REPLACE FUNCTION all_user_privileges() RETURNS SETOF all_privileges_type AS
$$
DECLARE
	_row text;
BEGIN
	FOR _row IN
        SELECT r.rolname FROM pg_catalog.pg_roles r WHERE r.rolname NOT IN ('information_schema','pg_catalog') AND r.rolname !~ '^pg_' AND r.rolname !~ '^rds' ORDER BY 1
    LOOP
		RETURN QUERY SELECT * FROM all_privileges(_row);
    END LOOP;
END
$$ LANGUAGE plpgsql;
ALTER FUNCTION all_user_privileges(text) OWNER TO <user_name>;
COMMENT ON FUNCTION all_user_privileges(text) IS 'This will list all privileges for all user (Database | Schema | Table | View | Sequence | Tablespace)';
