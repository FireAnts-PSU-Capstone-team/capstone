/*
This SQL file will be executed once the DB is set up.
*/

-------------------------
-- Functions
-------------------------

--
-- Name: change_fnc(); Type: FUNCTION; Schema: public; Owner: cc
-- Desc: Monitors table for any insert/update/delete commands
-- 		 It copies the old data and the new data in txn_history table as
--  	 JSON. In case of DELETE it copies data into archive table then updates txn_history
--       with location data for archive table
--
CREATE FUNCTION change_fnc() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$BEGIN
IF TG_OP='INSERT'
THEN
INSERT INTO txn_history(tabname,schemaname,operation, new_val)
VALUES(TG_RELNAME, TG_TABLE_SCHEMA, TG_OP, row_to_json(NEW));
RETURN NEW;
ELSIF TG_OP = 'UPDATE'
THEN
INSERT INTO txn_history(tabname,schemaname,operation, new_val, old_val)
VALUES(TG_RELNAME,TG_TABLE_SCHEMA, TG_OP, row_to_json(NEW), row_to_json(OLD));
RETURN NEW;
ELSIF TG_OP = 'DELETE'
THEN
INSERT INTO archive (old_val)
VALUES(row_to_json(OLD));
INSERT INTO txn_history(tabname,schemaname,operation, archive_row)
VALUES(TG_RELNAME,TG_TABLE_SCHEMA, TG_OP, (SELECT currval('archive_row_seq')));
RETURN OLD;
END IF;
END;
$$;

ALTER FUNCTION change_fnc() OWNER TO cc;

--
-- A TRIGGER for insert conflict strategy
-- Name: check_insertion_fnc; Type: TRIGGER; Schema: public; Owner: cc
--

--CREATE FUNCTION check_insertion_fnc()
--    RETURNS TRIGGER
--    LANGUAGE 'plpgsql'
--AS $BODY$
--BEGIN
--IF (SELECT count(*)
--   FROM intake
--   WHERE mrl = NEW.mrl) = 0
--THEN
--   RETURN NEW;
--ELSE
--   RETURN NULL;
--END IF;
--END;$BODY$;
--
--ALTER FUNCTION check_insertion_fnc() OWNER TO cc;

--
-- A function to restore a record from the archive table back to original table
-- Name: restore_record
--
CREATE OR REPLACE FUNCTION restore_row(row_num integer)
    RETURNS boolean
    LANGUAGE 'plpgsql'
AS $_$DECLARE
tablename text;
success integer;
BEGIN
SELECT t.tabname into tablename
from txn_history as t join archive as a
on t.archive_row = a.row_id
WHERE a.row_id = row_num;
IF NOT FOUND THEN
	RETURN FALSE;
END IF;
EXECUTE
format('INSERT INTO %I
SELECT *
FROM json_populate_record(NULL::%I, (SELECT old_val FROM archive WHERE row_id = $1))',tablename,tablename)
USING row_num;
GET DIAGNOSTICS success = ROW_COUNT;
IF success = 1
THEN
RETURN TRUE;
ELSE
RETURN FALSE;
END IF;
END;$_$;

ALTER FUNCTION restore_row(row_num integer) OWNER TO cc;


-------------------------
-- DB Parameters
-------------------------

SET default_tablespace = '';
SET default_table_access_method = heap;

-------------------------
-- Tables
-------------------------

--
-- Name: metadata; Type: TABLE; Schema: public; Owner: cc
--
CREATE TABLE IF NOT EXISTS metadata (
    filename TEXT NOT NULL,
    creator TEXT,
    size INT,
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,
    last_modified_by TEXT,
    title TEXT,
    "rows" INT,
    columns INT
);
ALTER TABLE metadata OWNER TO cc;
COMMENT ON TABLE metadata IS 'Table to track the file metadata that is uploaded to DB';

--
-- Name: Intake; Type: TABLE; Schema: public; Owner: cc
--
CREATE TABLE intake (
    "row" integer NOT NULL,
    submission_date date,
    entity text,
    dba text,
    facility_address text,
    facility_suite text,
    facility_zip text,
    mailing_address text,
    mrl character varying(10) UNIQUE,
    neighborhood_association character varying(30),
    compliance_region character varying(2),
    primary_contact_first_name text,
    primary_contact_last_name text,
    email text,
    phone character(12),
    endorse_type character(25),
    license_type character varying(25),
    repeat_location character(1),
    app_complete character varying(3),
    fee_schedule character varying(10),
    receipt_num integer UNIQUE,
    cash_amount text,
    check_amount text,
    card_amount text,
    check_num_approval_code character varying(25),
    mrl_num character varying(10),
    notes text,
    validation_errors text 
);
ALTER TABLE intake OWNER TO cc;
COMMENT ON TABLE intake IS 'Table to track all the data for cannabis program in city of portalnd';
ALTER TABLE ONLY intake
    ADD CONSTRAINT intake_pkey PRIMARY KEY ("row");
    
--
-- Name: txn_history; Type: TABLE; Schema: public; Owner: cc
--
CREATE TABLE txn_history (
    id integer NOT NULL,
    tstamp timestamp without time zone DEFAULT now(),
    schemaname text,
    operation text,
    who text DEFAULT CURRENT_USER,
    new_val json,
    old_val json,
    tabname text,
    archive_row integer
);
ALTER TABLE txn_history OWNER TO cc;
COMMENT ON TABLE txn_history IS 'Table tracks the changes made to the intake database table';
ALTER TABLE ONLY txn_history
    ADD CONSTRAINT txn_history_pkey PRIMARY KEY (id);
    
--
-- Name: archive; Type: TABLE; Schema: public; Owner: CC
--
CREATE TABLE archive (
    row_id integer NOT NULL,
    tstamp timestamp without time zone DEFAULT now(),
    who text DEFAULT CURRENT_USER,
    old_val json
);
ALTER TABLE archive OWNER TO cc;
COMMENT ON TABLE archive IS 'Table tracks the rows removed from the intake database table';
ALTER TABLE ONLY archive
    ADD CONSTRAINT archive_pkey PRIMARY KEY (row_id);

--
-- Name: violations Type: table Schema: public Owner: cc
--
CREATE TABLE IF NOT EXISTS violations
(
    "row" integer NOT NULL,
    dba text,
    address text,
    mrl_num text UNIQUE,
    license_type text,
    violation_sent_date date,
    original_violation_amount text,
    admin_rvw_decision_date date,
    admin_rvw_violation_amount text,
    certified_num text,
    certified_receipt_returned text,
    date_paid_waived date,
    receipt_no text UNIQUE,
    cash_amount text,
    check_amount text,
    card_amount text,
    check_num_approval_code text,
    notes text,
    validation_errors text 
);
ALTER TABLE violations OWNER to cc;
COMMENT ON TABLE violations IS 'Table to hold all the information regarding violations.';
ALTER TABLE ONLY violations
    ADD CONSTRAINT violations_pkey PRIMARY KEY ("row");

--
-- Name: records Type: table Schema: public Owner: cc
--
CREATE TABLE IF NOT EXISTS records
(
    "row" integer NOT NULL,
    date date,
    method text,
    intake_person text,
    rp_name text,
    rp_contact_info text,
    concern text,
    location_name text,
    address text,
    mrl_num text UNIQUE,
    action_taken text,
    status text,
    status_date date,
    additional_notes text,
    validation_errors text
);
ALTER TABLE records OWNER to cc;
COMMENT ON TABLE records IS 'Table to hold all the information regarding violations.';
ALTER TABLE ONLY records
    ADD CONSTRAINT records_pkey PRIMARY KEY ("row");
-------------------------
-- Sequences
-------------------------

--
-- Name: txn_history_id_seq
-- Desc: Sequence used as PK for txn_history table Owner: cc
--
CREATE SEQUENCE txn_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE txn_history_id_seq OWNER TO cc;
ALTER SEQUENCE txn_history_id_seq OWNED BY txn_history.id;
ALTER TABLE ONLY txn_history ALTER COLUMN id SET DEFAULT nextval('txn_history_id_seq'::regclass);

--
-- Name: archive_row_seq
-- Desc: Sequence used as PK for archive table Owner: cc
--
CREATE SEQUENCE archive_row_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE archive_row_seq OWNER TO cc;
ALTER SEQUENCE archive_row_seq OWNED BY archive.row_id;
ALTER TABLE ONLY archive ALTER COLUMN row_id SET DEFAULT nextval('archive_row_seq'::regclass);

-------------------------
-- Triggers
-------------------------

--
-- Name: intake_transactions
-- Desc: Monitor intake table, before any transaction calls function change_TRIGGER
--
CREATE TRIGGER intake_transactions
BEFORE INSERT OR UPDATE OR DELETE ON intake
FOR EACH ROW EXECUTE FUNCTION change_fnc();

--
-- Name: intake_check_insertion
-- Desc: Monitor intake table, before any INSERT calls function check_insertion_to_intake_tri_fnc
--
--CREATE TRIGGER intake_check_insertion
--BEFORE INSERT ON intake
--FOR EACH ROW EXECUTE FUNCTION check_insertion_fnc();

--
-- Name: violations_transactions
-- Desc: Monitor violations table, before any transaction calls function change_fnc
--
CREATE TRIGGER violations_transactions
BEFORE INSERT OR UPDATE OR DELETE ON violations
FOR EACH ROW EXECUTE FUNCTION change_fnc();

--
-- Name: records_transactions
-- Desc: Monitor records table, before any transaction calls function change_fnc
--
CREATE TRIGGER records_transactions
BEFORE INSERT OR UPDATE OR DELETE ON records
FOR EACH ROW EXECUTE FUNCTION change_fnc();

-------------------------
-- Groups
-------------------------

CREATE ROLE readaccess;
CREATE ROLE writeaccess;
CREATE ROLE adminaccess;

-------------------------
-- Users
-------------------------

CREATE USER reader WITH PASSWORD 'capstone';
CREATE USER writer WITH PASSWORD 'capstone';
CREATE USER administrator WITH PASSWORD 'capstone';

-------------------------
-- Access
-------------------------
REVOKE ALL ON SCHEMA public FROM public;

-- Read Group
GRANT USAGE ON SCHEMA public TO readaccess;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;

-- Write Group
GRANT USAGE ON SCHEMA public TO writeaccess;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO writeaccess;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public to writeaccess;

-- Admin Group
GRANT ALL PRIVILEGES ON SCHEMA public TO adminaccess;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adminaccess;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO adminaccess;

-- Grant group access
GRANT readaccess TO reader;
GRANT writeaccess TO writer;
GRANT adminaccess TO administrator;
