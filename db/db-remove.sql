/* 
remove all stuffs built in the current DB, used by restoring DB (called before restoring) 
to avoid additional errors
*/
DROP TRIGGER IF EXISTS transactions ON public.intake;

DROP TRIGGER IF EXISTS check_insertion ON public.intake;

DROP FUNCTION IF EXISTS change_trigger;

DROP FUNCTION IF EXISTS check_insertion_to_intake_tri_fnc;

DROP SEQUENCE IF EXISTS public.intake_row_seq CASCADE;

DROP SEQUENCE IF EXISTS public.txn_history_id_seq CASCADE;

DROP SEQUENCE IF EXISTS public.archive_row_seq CASCADE;

DROP TABLE IF EXISTS metadata;

DROP TABLE IF EXISTS intake;

DROP TABLE IF EXISTS txn_history;

DROP TABLE IF EXISTS archive;


