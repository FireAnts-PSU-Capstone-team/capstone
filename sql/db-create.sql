/*
This SQL file will be executed once the DB has set up.
*/

--
-- Name: change_trigger(); Type: FUNCTION; Schema: public; Owner: cc
-- Desc: Monitors the intake table for any insert or update commands
-- 		 It copys the old data and the new data in txn_history table as 
--  	 JSON.
--
CREATE FUNCTION change_trigger() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
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
END IF;
END;
$$;

ALTER FUNCTION change_trigger() OWNER TO cc;

--
-- Name: change_trigger(); Type: FUNCTION; Schema: public; Owner: cc
-- Desc: Monitors the intake table for any delete command. It copies the
-- 		 old data into the archive table, before removing it from the 
--		 intake table.
-- 
CREATE FUNCTION public.archive_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
IF TG_OP='DELETE'
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
RETURN OLD;
END IF;
END;$$;

ALTER FUNCTION archive_trigger() OWNER TO cc;



SET default_tablespace = '';

SET default_table_access_method = heap;


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
    title TEXT
);

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

SELECT pg_catalog.setval('intake_row_seq', 1, true);

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
    tabname text
);

ALTER TABLE txn_history OWNER TO cc;

COMMENT ON TABLE txn_history IS 'Table tracks the changes made to the intake database table';

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

SELECT pg_catalog.setval('txn_history_id_seq', 1, true);

ALTER TABLE ONLY txn_history
    ADD CONSTRAINT txn_history_pkey PRIMARY KEY (id);

--
-- Name: archive; Type: TABLE; Schema: public; Owner: CC
--
CREATE TABLE archive (
    row_id integer NOT NULL,
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

CREATE SEQUENCE archive_row_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE archive_row_seq OWNER TO cc;

ALTER SEQUENCE archive_row_seq OWNED BY archive.row_id;

ALTER TABLE ONLY archive ALTER COLUMN row_id SET DEFAULT nextval('archive_row_seq'::regclass);

ALTER TABLE ONLY archive
    ADD CONSTRAINT archive_pkey PRIMARY KEY (row_id);

--
-- Create triggers for archive and txn_history tables
--
CREATE TRIGGER update BEFORE INSERT OR UPDATE ON intake FOR EACH ROW EXECUTE FUNCTION change_trigger();
CREATE TRIGGER archive BEFORE DELETE ON intake FOR EACH ROW EXECUTE FUNCTION archive_trigger();

--
-- Create groups
--
CREATE ROLE readaccess;
CREATE ROLE writeaccess;
CREATE ROLE adminaccess;

--
-- Remove default permissions
--
REVOKE ALL ON SCHEMA public FROM public;


--
-- Name: Insert Sample Data; type: DATA; schema: public
--
INSERT INTO intake VALUES (DEFAULT,'2015-12-01 00:00:00', 'New Horizons Consultants, LLC', 'Home Grown Apothecary', '1937 NE Pacific St.', NULL, '97232', 'PO Box 212, Brightwood, OR 97011', 'MRL3', 'Kerns', 'N', 'Randa', 'Shahin', 'randa@homegrownapothecary.com', '503-484-7254', NULL, 'DRE-MD', NULL, NULL, '2015', 4, 975, NULL, NULL, NULL, 'MRL3', NULL);
INSERT INTO intake VALUES (DEFAULT,'2015-12-01 00:00:00', 'Blue Elephant Holdings, LLC', 'The Human Collective II', '9220 SW Barbur Blvd.', ' #107', '97219', '9220 SW Barbur Blvd. #107', 'MRL6', 'Southwest Neighborhood Inc', 'SW', 'Donald', 'Morse', 'don@humancollective.org', '503-956-1540', NULL, 'DRE-MD', NULL, NULL, '2015', 3, 975, NULL, NULL, NULL, 'MRL6', NULL);
INSERT INTO intake VALUES (DEFAULT, '2015-12-01 00:00:00', 'Rooted Northwest, Inc.', NULL, '7817 NE Halsey St.', NULL, '97213', '2534 NE 50th Ave.', 'MRL7', 'Montavilla', 'NE', 'Christopher', 'Olson', 'olsonpdx@yahoo.com', '503-780-4834', NULL, 'DRE-MD', NULL, NULL, '2015', 6, NULL, 975, NULL, '17-292176052', 'MRL7', NULL);


-- Grant access to read group
GRANT USAGE ON SCHEMA public TO readaccess;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;

-- Grant access to write group
GRANT USAGE ON SCHEMA public TO writeaccess;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO writeaccess;

-- Grant access to admin group
GRANT ALL PRIVILEGES ON SCHEMA public TO adminaccess;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adminaccess;

-- Create users
CREATE USER reader WITH PASSWORD 'capstone';
CREATE USER writer WITH PASSWORD 'capstone';
CREATE USER administrator WITH PASSWORD 'capstone';

-- Grant group access
GRANT readaccess TO reader;
GRANT writeaccess TO writer;
GRANT adminaccess TO administrator;
