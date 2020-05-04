/*
This SQL file will be executed once the DB is set up.
*/

-------------------------
-- Functions
-------------------------

--
-- Name: change_trigger(); Type: FUNCTION; Schema: public; Owner: cc
-- Desc: Monitors the intake table for any insert or update commands
-- 		 It copys the old data and the new data in txn_history table as 
--  	 JSON.
--
CREATE FUNCTION change_trigger() RETURNS trigger
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
INSERT INTO archive (old_row, old_submission_date, old_entity, old_dba,
	    old_facility_address, old_facility_suite, old_facility_zip,
		old_mailing_address, old_mrl, old_neighborhood_association,
		old_compliance_region, old_primary_contact_first_name,
		old_primary_contact_last_name,old_email,old_phone,
		old_endorse_type,old_license_type,old_repeat_location,
		old_app_complete,old_fee_schedule,old_receipt_num,
		old_cash_amount,old_check_amount,old_card_amount,
		old_check_num_approval_code,old_mrl_num,old_notes )
VALUES(OLD.row, OLD.submission_date, OLD.entity, OLD.dba,
	   OLD.facility_address, OLD.facility_suite, OLD.facility_zip,
		OLD.mailing_address, OLD.mrl, OLD.neighborhood_association,
		OLD.compliance_region, OLD.primary_contact_first_name,
		OLD.primary_contact_last_name,OLD.email,OLD.phone,
		OLD.endorse_type,OLD.license_type,OLD.repeat_location,
		OLD.app_complete,OLD.fee_schedule,OLD.receipt_num,
		OLD.cash_amount,OLD.check_amount,OLD.card_amount,
		OLD.check_num_approval_code,OLD.mrl_num,OLD.notes);
INSERT INTO txn_history(tabname,schemaname,operation, archive_row)
VALUES(TG_RELNAME,TG_TABLE_SCHEMA, TG_OP, (SELECT currval('archive_row_seq')));
RETURN OLD;
END IF;
END;
$$;

ALTER FUNCTION change_trigger() OWNER TO cc;

--
-- A trigger for insert conflict strategy
-- Name: check_insertion_to_intake_trigger; Type: TRIGGER; Schema: public; Owner: cc
--

CREATE FUNCTION check_insertion_to_intake_tri_fnc()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$BEGIN
CASE WHEN NEW.dba IS NULL
THEN
IF (SELECT count(*)
   FROM intake
   WHERE submission_date = new.submission_date
   AND entity = new.entity
   AND mrl = NEW.mrl) = 0
THEN
   RETURN NEW;
ELSE
   RETURN NULL;
END IF;
ELSE
IF (SELECT count(*)
   FROM intake
   WHERE submission_date = NEW.submission_date
   AND entity = NEW.entity
   AND dba = NEW.dba
   AND mrl = NEW.mrl) = 0
THEN
   RETURN NEW;
ELSE
   RETURN NULL;
END IF;
END CASE;
END;$BODY$;

ALTER FUNCTION check_insertion_to_intake_tri_fnc() OWNER TO cc;

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
    mrl character varying(10),
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
    receipt_num integer,
    cash_amount text,
    check_amount text,
    card_amount text,
    check_num_approval_code character varying(25),
    mrl_num character varying(10),
    notes text
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
    old_row integer,
    old_submission_date date,
    old_entity text,
    old_dba text,
    old_facility_address text,
    old_facility_suite text,
    old_facility_zip text,
    old_mailing_address text,
    old_mrl character varying(10),
    old_neighborhood_association character varying(30),
    old_compliance_region character varying(2),
    old_primary_contact_first_name text,
    old_primary_contact_last_name text,
    old_email text,
    old_phone character(12),
    old_endorse_type character(25),
    old_license_type character varying(25),
    old_repeat_location character(1),
    old_app_complete character varying(3),
    old_fee_schedule character varying(5),
    old_receipt_num integer,
    old_cash_amount text,
    old_check_amount text,
    old_card_amount text,
    old_check_num_approval_code character varying(25),
    old_mrl_num character varying(10),
    old_notes text
);
ALTER TABLE archive OWNER TO cc;
COMMENT ON TABLE archive IS 'Table tracks the rows removed from the intake database table';
ALTER TABLE ONLY archive
    ADD CONSTRAINT archive_pkey PRIMARY KEY (row_id);
    
-------------------------
-- Sequences
-------------------------

--
-- Name: intake_row_seq
-- Desc: Sequence used as PK for intake table Owner: cc
--
CREATE SEQUENCE intake_row_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE intake_row_seq OWNER TO cc;
ALTER SEQUENCE intake_row_seq OWNED BY intake."row";
ALTER TABLE ONLY intake ALTER COLUMN "row" SET DEFAULT nextval('intake_row_seq'::regclass);

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
-- Name: transactions
-- Desc: Monitor intake table, before any transaction calls function change_trigger
--
CREATE TRIGGER transactions 
BEFORE INSERT OR UPDATE OR DELETE ON intake 
FOR EACH ROW EXECUTE FUNCTION change_trigger();

--
-- Name: check_insertion
-- Desc: Monitor intake table, before any INSERT calls function check_insertion_to_intake_tri_fnc
--
CREATE TRIGGER check_insertion 
BEFORE INSERT ON intake 
FOR EACH ROW EXECUTE FUNCTION check_insertion_to_intake_tri_fnc();

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
