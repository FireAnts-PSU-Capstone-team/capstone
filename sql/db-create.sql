/*
This SQL file will be executed once the DB has set up.

*/--
-- PostgreSQL database dump
--

-- Name: change_trigger(); Type: FUNCTION; Schema: public; Owner: cc
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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 205 (class 1259 OID 355326)
-- Name: Intake; Type: TABLE; Schema: public; Owner: cc
--

CREATE TABLE IF NOT EXISTS metadata (
    filename TEXT NOT NULL,
    creator TEXT NOT NULL,
    size INT,
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,
    last_modified_by TEXT,
    title TEXT
);

CREATE TABLE intake (
     "row" integer NOT NULL,
    submission_date date,
    entity text,
    dba text,
    facility_address text,
    facility_suite text,
    facility_zip character(5),
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
    repeat_location character(1) DEFAULT 'N'::bpchar,
    app_complete character varying(3) DEFAULT 'N/A'::bpchar,
    fee_schedule character varying(5),
    receipt_num integer,
    cash_amount money DEFAULT 0,
    check_amount money DEFAULT 0,
    card_amount money DEFAULT 0,
    check_num_approval_code character varying(25),
    mrl_num character varying(10),
    notes text
);


ALTER TABLE intake OWNER TO cc;

--
-- TOC entry 204 (class 1259 OID 355324)
-- Name: Intake_row_seq; Type: SEQUENCE; Schema: public; Owner: cc
--

CREATE SEQUENCE intake_row_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE intake_row_seq OWNER TO cc;

--
-- TOC entry 3223 (class 0 OID 0)
-- Dependencies: 204
-- Name: Intake_row_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cc
--

ALTER SEQUENCE intake_row_seq OWNED BY intake."row";


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

-- Create groups
CREATE ROLE readaccess;
CREATE ROLE writeaccess;
CREATE ROLE adminaccess;

-- Remove default permissions
REVOKE ALL ON SCHEMA public FROM public;

ALTER TABLE txn_history OWNER TO cc;

--
-- TOC entry 3224 (class 0 OID 0)
-- Dependencies: 203
-- Name: TABLE txn_history; Type: COMMENT; Schema: public; Owner: cc
--

COMMENT ON TABLE txn_history IS 'Table tracks the changes made to the intake database table';


--
-- TOC entry 202 (class 1259 OID 355250)
-- Name: txn_history_id_seq; Type: SEQUENCE; Schema: public; Owner: cc
--

CREATE SEQUENCE txn_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE txn_history_id_seq OWNER TO cc;

--
-- TOC entry 3225 (class 0 OID 0)
-- Dependencies: 202
-- Name: txn_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cc
--

ALTER SEQUENCE txn_history_id_seq OWNED BY txn_history.id;


--
-- TOC entry 3076 (class 2604 OID 355329)
-- Name: Intake row; Type: DEFAULT; Schema: public; Owner: cc
--

ALTER TABLE ONLY intake ALTER COLUMN "row" SET DEFAULT nextval('intake_row_seq'::regclass);


--
-- TOC entry 3073 (class 2604 OID 355255)
-- Name: txn_history id; Type: DEFAULT; Schema: public; Owner: cc
--

ALTER TABLE ONLY txn_history ALTER COLUMN id SET DEFAULT nextval('txn_history_id_seq'::regclass);



--
-- TOC entry 3226 (class 0 OID 0)
-- Dependencies: 204
-- Name: Intake_row_seq; Type: SEQUENCE SET; Schema: public; Owner: cc
--

SELECT pg_catalog.setval('intake_row_seq', 1, true);


--
-- TOC entry 3227 (class 0 OID 0)
-- Dependencies: 202
-- Name: txn_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cc
--

SELECT pg_catalog.setval('txn_history_id_seq', 1, true);


--
-- TOC entry 3085 (class 2606 OID 355337)
-- Name: Intake Intake_pkey; Type: CONSTRAINT; Schema: public; Owner: cc
--

ALTER TABLE ONLY intake
    ADD CONSTRAINT intake_pkey PRIMARY KEY ("row");


--
-- TOC entry 3083 (class 2606 OID 355262)
-- Name: txn_history txn_history_pkey; Type: CONSTRAINT; Schema: public; Owner: cc
--

ALTER TABLE ONLY txn_history
    ADD CONSTRAINT txn_history_pkey PRIMARY KEY (id);


--
-- TOC entry 3086 (class 2620 OID 355444)
-- Name: Intake update; Type: TRIGGER; Schema: public; Owner: cc
--

CREATE TRIGGER update BEFORE INSERT OR UPDATE ON intake FOR EACH ROW EXECUTE FUNCTION change_trigger();

--
-- Name: Insert Sample Data; type: DATA; schema: public
--

INSERT INTO intake VALUES (DEFAULT,'2015-12-01 00:00:00', 'New Horizons Consultants, LLC', 'Home Grown Apothecary', '1937 NE Pacific St.', NULL, '97232', 'PO Box 212, Brightwood, OR 97011', 'MRL3', 'Kerns', 'N', 'Randa', 'Shahin', 'randa@homegrownapothecary.com', '503-484-7254', NULL, 'DRE-MD', NULL, NULL, '2015', 4, 975, NULL, NULL, NULL, 'MRL3', NULL);
INSERT INTO intake VALUES (DEFAULT,'2015-12-01 00:00:00', 'Blue Elephant Holdings, LLC', 'The Human Collective II', '9220 SW Barbur Blvd.', ' #107', '97219', '9220 SW Barbur Blvd. #107', 'MRL6', 'Southwest Neighborhood Inc', 'SW', 'Donald', 'Morse', 'don@humancollective.org', '503-956-1540', NULL, 'DRE-MD', NULL, NULL, '2015', 3, 975, NULL, NULL, NULL, 'MRL6', NULL);
INSERT INTO intake VALUES (DEFAULT, '2015-12-01 00:00:00', 'Rooted Northwest, Inc.', NULL, '7817 NE Halsey St.', NULL, '97213', '2534 NE 50th Ave.', 'MRL7', 'Montavilla', 'NE', 'Christopher', 'Olson', 'olsonpdx@yahoo.com', '503-780-4834', NULL, 'DRE-MD', NULL, NULL, '2015', 6, NULL, 975, NULL, '17-292176052', 'MRL7', NULL);

--
-- PostgreSQL database dump complete
--


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