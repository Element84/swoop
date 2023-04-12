SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: partman; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA partman;


--
-- Name: swoop; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA swoop;


--
-- Name: tap; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA tap;


--
-- Name: pg_partman; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;


--
-- Name: EXTENSION pg_partman; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_partman IS 'Extension to manage partitioned tables by time or ID';


--
-- Name: pgtap; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgtap WITH SCHEMA tap;


--
-- Name: EXTENSION pgtap; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgtap IS 'Unit testing for PostgreSQL';


--
-- Name: add_pending_event(); Type: FUNCTION; Schema: swoop; Owner: -
--

CREATE FUNCTION swoop.add_pending_event() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
BEGIN
  INSERT INTO swoop.event (event_time, action_uuid, status) VALUES
    (NEW.created_at, NEW.action_uuid, 'PENDING');
  RETURN NULL;
END;
$$;


--
-- Name: get_processable_actions(smallint, text[]); Type: FUNCTION; Schema: swoop; Owner: -
--

CREATE FUNCTION swoop.get_processable_actions(_limit smallint DEFAULT 10, _action_names text[] DEFAULT ARRAY[]::text[]) RETURNS TABLE(action_uuid uuid, action_name text)
    LANGUAGE plpgsql
    AS $$
DECLARE
BEGIN
  RETURN QUERY SELECT
    a.action_uuid,
    a.action_name
  FROM
    swoop.action_thread as a
  WHERE
    a.is_processable
    AND (
      array_length(_action_names, 1) = 0
      OR a.action_name = any(_action_names)
    )
    AND pg_try_advisory_lock(to_regclass('swoop.thread')::oid::integer, a.lock_id)
  LIMIT _limit;
  RETURN;
END;
$$;


--
-- Name: release_processable_lock(uuid); Type: FUNCTION; Schema: swoop; Owner: -
--

CREATE FUNCTION swoop.release_processable_lock(_action_uuid uuid) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
BEGIN
  RETURN (
    SELECT
      pg_advisory_unlock(to_regclass('swoop.thread')::oid::integer, lock_id)
    FROM
      swoop.thread as t
    WHERE
      t.action_uuid = _action_uuid
  );
END;
$$;


--
-- Name: update_thread(); Type: FUNCTION; Schema: swoop; Owner: -
--

CREATE FUNCTION swoop.update_thread() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  _latest timestamptz;
  _status text;
  _next_attempt timestamptz;
BEGIN
  -- get the latest event time for the action thread
  SELECT last_update FROM swoop.thread where action_uuid = NEW.action_uuid INTO _latest;

  -- if the event time is older than the last update we don't update the thread
  IF _latest IS NOT NULL AND NEW.event_time < _latest THEN
    RETURN NULL;
  END IF;

  -- coerce status to UNKNOWN if it doesn't match a known status type
  SELECT name from swoop.event_state WHERE name = NEW.status
  UNION
  SELECT 'UNKNOWN'
  LIMIT 1
  INTO _status;

  -- if we need a next attempt time let's calculated it
  IF NEW.retry_seconds IS NOT NULL THEN
    SELECT NEW.event_time + (NEW.retry_seconds * interval '1 second') INTO _next_attempt;
  END IF;

  IF _latest IS NULL THEN
    INSERT INTO swoop.thread (created_at, last_update, action_uuid, status, next_attempt_after)
      VALUES (NEW.event_time, NEW.event_time, NEW.action_uuid, _status, _next_attempt);
  ELSE
    UPDATE swoop.thread as t SET
      last_update = NEW.event_time,
      status = _status,
      next_attempt_after = _next_attempt
    WHERE
      t.action_uuid = NEW.action_uuid;
  END IF;

  RETURN NULL;
END;
$$;


SET default_tablespace = '';

--
-- Name: action; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
)
PARTITION BY RANGE (created_at);


SET default_table_access_method = heap;

--
-- Name: action_default; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_default (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2022_12; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2022_12 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_01; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_01 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_02; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_02 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_03; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_03 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_04; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_04 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_05; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_05 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_06; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_06 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_07; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_07 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_p2023_08; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_p2023_08 (
    action_uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    priority smallint DEFAULT 100,
    CONSTRAINT action_action_type_check CHECK ((action_type = ANY (ARRAY['callback'::text, 'workflow'::text]))),
    CONSTRAINT workflow_or_callback CHECK (
CASE
    WHEN (action_type = 'callback'::text) THEN ((parent_uuid IS NOT NULL) AND (workflow_name IS NULL))
    WHEN (action_type = 'workflow'::text) THEN (workflow_name IS NOT NULL)
    ELSE NULL::boolean
END)
);


--
-- Name: action_template; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.action_template (
    action_uuid uuid NOT NULL,
    action_type text NOT NULL,
    action_name text NOT NULL,
    parent_uuid bigint,
    workflow_name text,
    created_at timestamp with time zone NOT NULL,
    priority smallint
);


--
-- Name: thread; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
)
PARTITION BY RANGE (created_at);


--
-- Name: action_thread; Type: VIEW; Schema: swoop; Owner: -
--

CREATE VIEW swoop.action_thread AS
 SELECT a.action_uuid,
    a.action_type,
    a.action_name,
    a.parent_uuid,
    a.workflow_name,
    a.created_at,
    a.priority,
    t.last_update,
    t.status,
    t.next_attempt_after,
    t.lock_id,
    ((t.status = 'PENDING'::text) OR ((t.status = 'BACKOFF'::text) AND (t.next_attempt_after <= now()))) AS is_processable
   FROM (swoop.thread t
     JOIN swoop.action a USING (action_uuid));


--
-- Name: event; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
)
PARTITION BY RANGE (event_time);


--
-- Name: event_default; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_default (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2022_12; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2022_12 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_01; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_01 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_02; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_02 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_03; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_03 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_04; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_04 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_05; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_05 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_06; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_06 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_07; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_07 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_p2023_08; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_p2023_08 (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text,
    CONSTRAINT event_retry_seconds_check CHECK (((retry_seconds > 0) AND (retry_seconds <= 86400)))
);


--
-- Name: event_state; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_state (
    name text NOT NULL,
    description text NOT NULL
);


--
-- Name: event_template; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.event_template (
    event_time timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    retry_seconds integer,
    error text
);


--
-- Name: schema_migrations; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: thread_default; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_default (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_lock_id_seq; Type: SEQUENCE; Schema: swoop; Owner: -
--

ALTER TABLE swoop.thread ALTER COLUMN lock_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME swoop.thread_lock_id_seq
    START WITH 1
    INCREMENT BY 1
    MINVALUE -2147483648
    NO MAXVALUE
    CACHE 1
    CYCLE
);


--
-- Name: thread_p2022_12; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2022_12 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_01; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_01 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_02; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_02 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_03; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_03 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_04; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_04 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_05; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_05 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_06; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_06 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_07; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_07 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_p2023_08; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_p2023_08 (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: thread_template; Type: TABLE; Schema: swoop; Owner: -
--

CREATE TABLE swoop.thread_template (
    created_at timestamp with time zone NOT NULL,
    last_update timestamp with time zone NOT NULL,
    action_uuid uuid NOT NULL,
    status text NOT NULL,
    next_attempt_after timestamp with time zone,
    lock_id integer NOT NULL
);


--
-- Name: action_default; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_default DEFAULT;


--
-- Name: action_p2022_12; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2022_12 FOR VALUES FROM ('2022-12-01 00:00:00+00') TO ('2023-01-01 00:00:00+00');


--
-- Name: action_p2023_01; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_01 FOR VALUES FROM ('2023-01-01 00:00:00+00') TO ('2023-02-01 00:00:00+00');


--
-- Name: action_p2023_02; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_02 FOR VALUES FROM ('2023-02-01 00:00:00+00') TO ('2023-03-01 00:00:00+00');


--
-- Name: action_p2023_03; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_03 FOR VALUES FROM ('2023-03-01 00:00:00+00') TO ('2023-04-01 00:00:00+00');


--
-- Name: action_p2023_04; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_04 FOR VALUES FROM ('2023-04-01 00:00:00+00') TO ('2023-05-01 00:00:00+00');


--
-- Name: action_p2023_05; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_05 FOR VALUES FROM ('2023-05-01 00:00:00+00') TO ('2023-06-01 00:00:00+00');


--
-- Name: action_p2023_06; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_06 FOR VALUES FROM ('2023-06-01 00:00:00+00') TO ('2023-07-01 00:00:00+00');


--
-- Name: action_p2023_07; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_07 FOR VALUES FROM ('2023-07-01 00:00:00+00') TO ('2023-08-01 00:00:00+00');


--
-- Name: action_p2023_08; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action ATTACH PARTITION swoop.action_p2023_08 FOR VALUES FROM ('2023-08-01 00:00:00+00') TO ('2023-09-01 00:00:00+00');


--
-- Name: event_default; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_default DEFAULT;


--
-- Name: event_p2022_12; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2022_12 FOR VALUES FROM ('2022-12-01 00:00:00+00') TO ('2023-01-01 00:00:00+00');


--
-- Name: event_p2023_01; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_01 FOR VALUES FROM ('2023-01-01 00:00:00+00') TO ('2023-02-01 00:00:00+00');


--
-- Name: event_p2023_02; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_02 FOR VALUES FROM ('2023-02-01 00:00:00+00') TO ('2023-03-01 00:00:00+00');


--
-- Name: event_p2023_03; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_03 FOR VALUES FROM ('2023-03-01 00:00:00+00') TO ('2023-04-01 00:00:00+00');


--
-- Name: event_p2023_04; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_04 FOR VALUES FROM ('2023-04-01 00:00:00+00') TO ('2023-05-01 00:00:00+00');


--
-- Name: event_p2023_05; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_05 FOR VALUES FROM ('2023-05-01 00:00:00+00') TO ('2023-06-01 00:00:00+00');


--
-- Name: event_p2023_06; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_06 FOR VALUES FROM ('2023-06-01 00:00:00+00') TO ('2023-07-01 00:00:00+00');


--
-- Name: event_p2023_07; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_07 FOR VALUES FROM ('2023-07-01 00:00:00+00') TO ('2023-08-01 00:00:00+00');


--
-- Name: event_p2023_08; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event ATTACH PARTITION swoop.event_p2023_08 FOR VALUES FROM ('2023-08-01 00:00:00+00') TO ('2023-09-01 00:00:00+00');


--
-- Name: thread_default; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_default DEFAULT;


--
-- Name: thread_p2022_12; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2022_12 FOR VALUES FROM ('2022-12-01 00:00:00+00') TO ('2023-01-01 00:00:00+00');


--
-- Name: thread_p2023_01; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_01 FOR VALUES FROM ('2023-01-01 00:00:00+00') TO ('2023-02-01 00:00:00+00');


--
-- Name: thread_p2023_02; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_02 FOR VALUES FROM ('2023-02-01 00:00:00+00') TO ('2023-03-01 00:00:00+00');


--
-- Name: thread_p2023_03; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_03 FOR VALUES FROM ('2023-03-01 00:00:00+00') TO ('2023-04-01 00:00:00+00');


--
-- Name: thread_p2023_04; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_04 FOR VALUES FROM ('2023-04-01 00:00:00+00') TO ('2023-05-01 00:00:00+00');


--
-- Name: thread_p2023_05; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_05 FOR VALUES FROM ('2023-05-01 00:00:00+00') TO ('2023-06-01 00:00:00+00');


--
-- Name: thread_p2023_06; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_06 FOR VALUES FROM ('2023-06-01 00:00:00+00') TO ('2023-07-01 00:00:00+00');


--
-- Name: thread_p2023_07; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_07 FOR VALUES FROM ('2023-07-01 00:00:00+00') TO ('2023-08-01 00:00:00+00');


--
-- Name: thread_p2023_08; Type: TABLE ATTACH; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread ATTACH PARTITION swoop.thread_p2023_08 FOR VALUES FROM ('2023-08-01 00:00:00+00') TO ('2023-09-01 00:00:00+00');


--
-- Name: action_template action_template_pkey; Type: CONSTRAINT; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.action_template
    ADD CONSTRAINT action_template_pkey PRIMARY KEY (action_uuid);


--
-- Name: event_state event_state_pkey; Type: CONSTRAINT; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.event_state
    ADD CONSTRAINT event_state_pkey PRIMARY KEY (name);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: thread_template thread_template_pkey; Type: CONSTRAINT; Schema: swoop; Owner: -
--

ALTER TABLE ONLY swoop.thread_template
    ADD CONSTRAINT thread_template_pkey PRIMARY KEY (action_uuid);


--
-- Name: action_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_action_name_idx ON ONLY swoop.action USING btree (action_name);


--
-- Name: action_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_action_uuid_idx ON ONLY swoop.action USING btree (action_uuid);


--
-- Name: action_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_created_at_idx ON ONLY swoop.action USING btree (created_at);


--
-- Name: action_default_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_default_action_name_idx ON swoop.action_default USING btree (action_name);


--
-- Name: action_default_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_default_action_uuid_idx ON swoop.action_default USING btree (action_uuid);


--
-- Name: action_default_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_default_created_at_idx ON swoop.action_default USING btree (created_at);


--
-- Name: action_p2022_12_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2022_12_action_name_idx ON swoop.action_p2022_12 USING btree (action_name);


--
-- Name: action_p2022_12_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2022_12_action_uuid_idx ON swoop.action_p2022_12 USING btree (action_uuid);


--
-- Name: action_p2022_12_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2022_12_created_at_idx ON swoop.action_p2022_12 USING btree (created_at);


--
-- Name: action_p2023_01_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_01_action_name_idx ON swoop.action_p2023_01 USING btree (action_name);


--
-- Name: action_p2023_01_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_01_action_uuid_idx ON swoop.action_p2023_01 USING btree (action_uuid);


--
-- Name: action_p2023_01_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_01_created_at_idx ON swoop.action_p2023_01 USING btree (created_at);


--
-- Name: action_p2023_02_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_02_action_name_idx ON swoop.action_p2023_02 USING btree (action_name);


--
-- Name: action_p2023_02_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_02_action_uuid_idx ON swoop.action_p2023_02 USING btree (action_uuid);


--
-- Name: action_p2023_02_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_02_created_at_idx ON swoop.action_p2023_02 USING btree (created_at);


--
-- Name: action_p2023_03_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_03_action_name_idx ON swoop.action_p2023_03 USING btree (action_name);


--
-- Name: action_p2023_03_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_03_action_uuid_idx ON swoop.action_p2023_03 USING btree (action_uuid);


--
-- Name: action_p2023_03_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_03_created_at_idx ON swoop.action_p2023_03 USING btree (created_at);


--
-- Name: action_p2023_04_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_04_action_name_idx ON swoop.action_p2023_04 USING btree (action_name);


--
-- Name: action_p2023_04_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_04_action_uuid_idx ON swoop.action_p2023_04 USING btree (action_uuid);


--
-- Name: action_p2023_04_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_04_created_at_idx ON swoop.action_p2023_04 USING btree (created_at);


--
-- Name: action_p2023_05_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_05_action_name_idx ON swoop.action_p2023_05 USING btree (action_name);


--
-- Name: action_p2023_05_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_05_action_uuid_idx ON swoop.action_p2023_05 USING btree (action_uuid);


--
-- Name: action_p2023_05_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_05_created_at_idx ON swoop.action_p2023_05 USING btree (created_at);


--
-- Name: action_p2023_06_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_06_action_name_idx ON swoop.action_p2023_06 USING btree (action_name);


--
-- Name: action_p2023_06_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_06_action_uuid_idx ON swoop.action_p2023_06 USING btree (action_uuid);


--
-- Name: action_p2023_06_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_06_created_at_idx ON swoop.action_p2023_06 USING btree (created_at);


--
-- Name: action_p2023_07_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_07_action_name_idx ON swoop.action_p2023_07 USING btree (action_name);


--
-- Name: action_p2023_07_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_07_action_uuid_idx ON swoop.action_p2023_07 USING btree (action_uuid);


--
-- Name: action_p2023_07_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_07_created_at_idx ON swoop.action_p2023_07 USING btree (created_at);


--
-- Name: action_p2023_08_action_name_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_08_action_name_idx ON swoop.action_p2023_08 USING btree (action_name);


--
-- Name: action_p2023_08_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_08_action_uuid_idx ON swoop.action_p2023_08 USING btree (action_uuid);


--
-- Name: action_p2023_08_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX action_p2023_08_created_at_idx ON swoop.action_p2023_08 USING btree (created_at);


--
-- Name: event_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_action_uuid_idx ON ONLY swoop.event USING btree (action_uuid);


--
-- Name: event_default_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_default_action_uuid_idx ON swoop.event_default USING btree (action_uuid);


--
-- Name: event_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_event_time_idx ON ONLY swoop.event USING btree (event_time);


--
-- Name: event_default_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_default_event_time_idx ON swoop.event_default USING btree (event_time);


--
-- Name: event_p2022_12_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2022_12_action_uuid_idx ON swoop.event_p2022_12 USING btree (action_uuid);


--
-- Name: event_p2022_12_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2022_12_event_time_idx ON swoop.event_p2022_12 USING btree (event_time);


--
-- Name: event_p2023_01_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_01_action_uuid_idx ON swoop.event_p2023_01 USING btree (action_uuid);


--
-- Name: event_p2023_01_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_01_event_time_idx ON swoop.event_p2023_01 USING btree (event_time);


--
-- Name: event_p2023_02_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_02_action_uuid_idx ON swoop.event_p2023_02 USING btree (action_uuid);


--
-- Name: event_p2023_02_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_02_event_time_idx ON swoop.event_p2023_02 USING btree (event_time);


--
-- Name: event_p2023_03_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_03_action_uuid_idx ON swoop.event_p2023_03 USING btree (action_uuid);


--
-- Name: event_p2023_03_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_03_event_time_idx ON swoop.event_p2023_03 USING btree (event_time);


--
-- Name: event_p2023_04_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_04_action_uuid_idx ON swoop.event_p2023_04 USING btree (action_uuid);


--
-- Name: event_p2023_04_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_04_event_time_idx ON swoop.event_p2023_04 USING btree (event_time);


--
-- Name: event_p2023_05_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_05_action_uuid_idx ON swoop.event_p2023_05 USING btree (action_uuid);


--
-- Name: event_p2023_05_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_05_event_time_idx ON swoop.event_p2023_05 USING btree (event_time);


--
-- Name: event_p2023_06_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_06_action_uuid_idx ON swoop.event_p2023_06 USING btree (action_uuid);


--
-- Name: event_p2023_06_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_06_event_time_idx ON swoop.event_p2023_06 USING btree (event_time);


--
-- Name: event_p2023_07_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_07_action_uuid_idx ON swoop.event_p2023_07 USING btree (action_uuid);


--
-- Name: event_p2023_07_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_07_event_time_idx ON swoop.event_p2023_07 USING btree (event_time);


--
-- Name: event_p2023_08_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_08_action_uuid_idx ON swoop.event_p2023_08 USING btree (action_uuid);


--
-- Name: event_p2023_08_event_time_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX event_p2023_08_event_time_idx ON swoop.event_p2023_08 USING btree (event_time);


--
-- Name: thread_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_action_uuid_idx ON ONLY swoop.thread USING btree (action_uuid);


--
-- Name: thread_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_created_at_idx ON ONLY swoop.thread USING btree (created_at);


--
-- Name: thread_default_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_default_action_uuid_idx ON swoop.thread_default USING btree (action_uuid);


--
-- Name: thread_default_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_default_created_at_idx ON swoop.thread_default USING btree (created_at);


--
-- Name: thread_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_status_idx ON ONLY swoop.thread USING btree (status);


--
-- Name: thread_default_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_default_status_idx ON swoop.thread_default USING btree (status);


--
-- Name: thread_p2022_12_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2022_12_action_uuid_idx ON swoop.thread_p2022_12 USING btree (action_uuid);


--
-- Name: thread_p2022_12_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2022_12_created_at_idx ON swoop.thread_p2022_12 USING btree (created_at);


--
-- Name: thread_p2022_12_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2022_12_status_idx ON swoop.thread_p2022_12 USING btree (status);


--
-- Name: thread_p2023_01_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_01_action_uuid_idx ON swoop.thread_p2023_01 USING btree (action_uuid);


--
-- Name: thread_p2023_01_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_01_created_at_idx ON swoop.thread_p2023_01 USING btree (created_at);


--
-- Name: thread_p2023_01_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_01_status_idx ON swoop.thread_p2023_01 USING btree (status);


--
-- Name: thread_p2023_02_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_02_action_uuid_idx ON swoop.thread_p2023_02 USING btree (action_uuid);


--
-- Name: thread_p2023_02_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_02_created_at_idx ON swoop.thread_p2023_02 USING btree (created_at);


--
-- Name: thread_p2023_02_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_02_status_idx ON swoop.thread_p2023_02 USING btree (status);


--
-- Name: thread_p2023_03_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_03_action_uuid_idx ON swoop.thread_p2023_03 USING btree (action_uuid);


--
-- Name: thread_p2023_03_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_03_created_at_idx ON swoop.thread_p2023_03 USING btree (created_at);


--
-- Name: thread_p2023_03_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_03_status_idx ON swoop.thread_p2023_03 USING btree (status);


--
-- Name: thread_p2023_04_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_04_action_uuid_idx ON swoop.thread_p2023_04 USING btree (action_uuid);


--
-- Name: thread_p2023_04_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_04_created_at_idx ON swoop.thread_p2023_04 USING btree (created_at);


--
-- Name: thread_p2023_04_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_04_status_idx ON swoop.thread_p2023_04 USING btree (status);


--
-- Name: thread_p2023_05_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_05_action_uuid_idx ON swoop.thread_p2023_05 USING btree (action_uuid);


--
-- Name: thread_p2023_05_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_05_created_at_idx ON swoop.thread_p2023_05 USING btree (created_at);


--
-- Name: thread_p2023_05_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_05_status_idx ON swoop.thread_p2023_05 USING btree (status);


--
-- Name: thread_p2023_06_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_06_action_uuid_idx ON swoop.thread_p2023_06 USING btree (action_uuid);


--
-- Name: thread_p2023_06_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_06_created_at_idx ON swoop.thread_p2023_06 USING btree (created_at);


--
-- Name: thread_p2023_06_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_06_status_idx ON swoop.thread_p2023_06 USING btree (status);


--
-- Name: thread_p2023_07_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_07_action_uuid_idx ON swoop.thread_p2023_07 USING btree (action_uuid);


--
-- Name: thread_p2023_07_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_07_created_at_idx ON swoop.thread_p2023_07 USING btree (created_at);


--
-- Name: thread_p2023_07_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_07_status_idx ON swoop.thread_p2023_07 USING btree (status);


--
-- Name: thread_p2023_08_action_uuid_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_08_action_uuid_idx ON swoop.thread_p2023_08 USING btree (action_uuid);


--
-- Name: thread_p2023_08_created_at_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_08_created_at_idx ON swoop.thread_p2023_08 USING btree (created_at);


--
-- Name: thread_p2023_08_status_idx; Type: INDEX; Schema: swoop; Owner: -
--

CREATE INDEX thread_p2023_08_status_idx ON swoop.thread_p2023_08 USING btree (status);


--
-- Name: action_default_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_default_action_name_idx;


--
-- Name: action_default_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_default_action_uuid_idx;


--
-- Name: action_default_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_default_created_at_idx;


--
-- Name: action_p2022_12_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2022_12_action_name_idx;


--
-- Name: action_p2022_12_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2022_12_action_uuid_idx;


--
-- Name: action_p2022_12_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2022_12_created_at_idx;


--
-- Name: action_p2023_01_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_01_action_name_idx;


--
-- Name: action_p2023_01_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_01_action_uuid_idx;


--
-- Name: action_p2023_01_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_01_created_at_idx;


--
-- Name: action_p2023_02_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_02_action_name_idx;


--
-- Name: action_p2023_02_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_02_action_uuid_idx;


--
-- Name: action_p2023_02_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_02_created_at_idx;


--
-- Name: action_p2023_03_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_03_action_name_idx;


--
-- Name: action_p2023_03_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_03_action_uuid_idx;


--
-- Name: action_p2023_03_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_03_created_at_idx;


--
-- Name: action_p2023_04_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_04_action_name_idx;


--
-- Name: action_p2023_04_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_04_action_uuid_idx;


--
-- Name: action_p2023_04_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_04_created_at_idx;


--
-- Name: action_p2023_05_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_05_action_name_idx;


--
-- Name: action_p2023_05_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_05_action_uuid_idx;


--
-- Name: action_p2023_05_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_05_created_at_idx;


--
-- Name: action_p2023_06_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_06_action_name_idx;


--
-- Name: action_p2023_06_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_06_action_uuid_idx;


--
-- Name: action_p2023_06_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_06_created_at_idx;


--
-- Name: action_p2023_07_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_07_action_name_idx;


--
-- Name: action_p2023_07_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_07_action_uuid_idx;


--
-- Name: action_p2023_07_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_07_created_at_idx;


--
-- Name: action_p2023_08_action_name_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_name_idx ATTACH PARTITION swoop.action_p2023_08_action_name_idx;


--
-- Name: action_p2023_08_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_action_uuid_idx ATTACH PARTITION swoop.action_p2023_08_action_uuid_idx;


--
-- Name: action_p2023_08_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.action_created_at_idx ATTACH PARTITION swoop.action_p2023_08_created_at_idx;


--
-- Name: event_default_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_default_action_uuid_idx;


--
-- Name: event_default_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_default_event_time_idx;


--
-- Name: event_p2022_12_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2022_12_action_uuid_idx;


--
-- Name: event_p2022_12_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2022_12_event_time_idx;


--
-- Name: event_p2023_01_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_01_action_uuid_idx;


--
-- Name: event_p2023_01_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_01_event_time_idx;


--
-- Name: event_p2023_02_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_02_action_uuid_idx;


--
-- Name: event_p2023_02_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_02_event_time_idx;


--
-- Name: event_p2023_03_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_03_action_uuid_idx;


--
-- Name: event_p2023_03_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_03_event_time_idx;


--
-- Name: event_p2023_04_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_04_action_uuid_idx;


--
-- Name: event_p2023_04_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_04_event_time_idx;


--
-- Name: event_p2023_05_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_05_action_uuid_idx;


--
-- Name: event_p2023_05_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_05_event_time_idx;


--
-- Name: event_p2023_06_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_06_action_uuid_idx;


--
-- Name: event_p2023_06_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_06_event_time_idx;


--
-- Name: event_p2023_07_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_07_action_uuid_idx;


--
-- Name: event_p2023_07_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_07_event_time_idx;


--
-- Name: event_p2023_08_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_action_uuid_idx ATTACH PARTITION swoop.event_p2023_08_action_uuid_idx;


--
-- Name: event_p2023_08_event_time_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.event_event_time_idx ATTACH PARTITION swoop.event_p2023_08_event_time_idx;


--
-- Name: thread_default_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_default_action_uuid_idx;


--
-- Name: thread_default_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_default_created_at_idx;


--
-- Name: thread_default_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_default_status_idx;


--
-- Name: thread_p2022_12_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2022_12_action_uuid_idx;


--
-- Name: thread_p2022_12_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2022_12_created_at_idx;


--
-- Name: thread_p2022_12_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2022_12_status_idx;


--
-- Name: thread_p2023_01_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_01_action_uuid_idx;


--
-- Name: thread_p2023_01_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_01_created_at_idx;


--
-- Name: thread_p2023_01_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_01_status_idx;


--
-- Name: thread_p2023_02_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_02_action_uuid_idx;


--
-- Name: thread_p2023_02_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_02_created_at_idx;


--
-- Name: thread_p2023_02_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_02_status_idx;


--
-- Name: thread_p2023_03_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_03_action_uuid_idx;


--
-- Name: thread_p2023_03_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_03_created_at_idx;


--
-- Name: thread_p2023_03_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_03_status_idx;


--
-- Name: thread_p2023_04_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_04_action_uuid_idx;


--
-- Name: thread_p2023_04_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_04_created_at_idx;


--
-- Name: thread_p2023_04_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_04_status_idx;


--
-- Name: thread_p2023_05_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_05_action_uuid_idx;


--
-- Name: thread_p2023_05_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_05_created_at_idx;


--
-- Name: thread_p2023_05_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_05_status_idx;


--
-- Name: thread_p2023_06_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_06_action_uuid_idx;


--
-- Name: thread_p2023_06_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_06_created_at_idx;


--
-- Name: thread_p2023_06_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_06_status_idx;


--
-- Name: thread_p2023_07_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_07_action_uuid_idx;


--
-- Name: thread_p2023_07_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_07_created_at_idx;


--
-- Name: thread_p2023_07_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_07_status_idx;


--
-- Name: thread_p2023_08_action_uuid_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_action_uuid_idx ATTACH PARTITION swoop.thread_p2023_08_action_uuid_idx;


--
-- Name: thread_p2023_08_created_at_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_created_at_idx ATTACH PARTITION swoop.thread_p2023_08_created_at_idx;


--
-- Name: thread_p2023_08_status_idx; Type: INDEX ATTACH; Schema: swoop; Owner: -
--

ALTER INDEX swoop.thread_status_idx ATTACH PARTITION swoop.thread_p2023_08_status_idx;


--
-- Name: action add_pending_event; Type: TRIGGER; Schema: swoop; Owner: -
--

CREATE TRIGGER add_pending_event AFTER INSERT ON swoop.action FOR EACH ROW EXECUTE FUNCTION swoop.add_pending_event();


--
-- Name: event update_thread; Type: TRIGGER; Schema: swoop; Owner: -
--

CREATE TRIGGER update_thread AFTER INSERT ON swoop.event FOR EACH ROW EXECUTE FUNCTION swoop.update_thread();


--
-- Name: thread thread_status_fkey; Type: FK CONSTRAINT; Schema: swoop; Owner: -
--

ALTER TABLE swoop.thread
    ADD CONSTRAINT thread_status_fkey FOREIGN KEY (status) REFERENCES swoop.event_state(name) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO swoop.schema_migrations (version) VALUES
    ('20230412000000'),
    ('20230413043942');
