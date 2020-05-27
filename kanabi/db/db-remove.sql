/* 
remove all stuffs built in the current DB, used by restoring DB (called before restoring) 
to avoid additional errors
*/
DROP TRIGGER IF EXISTS intake_transactions ON public.intake;

DROP TRIGGER IF EXISTS intake_check_insertion ON public.intake;

DROP TRIGGER IF EXISTS violations_transactions ON public.violations;

DROP TRIGGER IF EXISTS records_transactions ON records;

DROP FUNCTION IF EXISTS change_fnc;

DROP FUNCTION IF EXISTS check_insertion_fnc;

DROP SEQUENCE IF EXISTS public.intake_row_seq CASCADE;

DROP SEQUENCE IF EXISTS public.txn_history_id_seq CASCADE;

DROP SEQUENCE IF EXISTS public.archive_row_seq CASCADE;

DROP SEQUENCE IF EXISTS public.violations_row_seq CASCADE;

DROP SEQUENCE IF EXISTS public.records_row_seq CASCADE;

DROP TABLE IF EXISTS metadata;

DROP TABLE IF EXISTS intake;

DROP TABLE IF EXISTS txn_history;

DROP TABLE IF EXISTS archive;

DROP TABLE IF EXISTS violations;

DROP TABLE IF EXISTS records;


