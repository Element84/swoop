-- migrate:up

CREATE SCHEMA IF NOT EXISTS swoop;
CREATE SCHEMA partman;
CREATE EXTENSION pg_partman SCHEMA partman;
CREATE SCHEMA tap;
CREATE EXTENSION pgtap SCHEMA tap;


CREATE TABLE IF NOT EXISTS swoop.event_state (
  name text PRIMARY KEY,
  description text NOT NULL
);

INSERT INTO swoop.event_state (name, description) VALUES
('PENDING', 'Action created and waiting to be executed'),
('QUEUED', 'Action queued for handler'),
('RUNNING', 'Action being run by handler'),
('SUCCESSFUL', 'Action successful'),
('FAILED', 'Action failed'),
('CANCELED', 'Action canceled'),
('TIMED_OUT', 'Action did not complete within allowed timeframe'),
('UNKNOWN', 'Last update was unknown state'),
('BACKOFF', 'Transient error, waiting to retry'),
(
  'INVALID',
  'Action could not be completed successfully due to '
  || 'configuration error or other incompatibility.'
),
(
  'RETRIES_EXHAUSTED',
  'Call did not fail within allowed time or number of retries'
);


CREATE TABLE IF NOT EXISTS swoop.action (
  action_uuid uuid NOT NULL DEFAULT gen_random_uuid(),
  action_type text NOT NULL CHECK (action_type IN ('callback', 'workflow')),
  action_name text NOT NULL,
  parent_uuid bigint, -- reference omitted, we don't need referential integrity
  workflow_name text,  -- not explicitly required, but helpful for queries
  created_at timestamptz NOT NULL DEFAULT now(),
  priority smallint DEFAULT 100,

  -- this is the key reason why workflows and callbacks are different
  CONSTRAINT workflow_or_callback CHECK (
    CASE
      WHEN
        action_type = 'callback' THEN
        parent_uuid IS NOT NULL
        AND workflow_name IS NULL
      WHEN
        action_type = 'workflow' THEN
        workflow_name IS NOT NULL
    END
  )
) PARTITION BY RANGE (created_at);

CREATE INDEX ON swoop.action (created_at);
CREATE INDEX ON swoop.action (action_uuid);
CREATE INDEX ON swoop.action (action_name);
CREATE TABLE IF NOT EXISTS swoop.action_template (LIKE swoop.action);
ALTER TABLE swoop.action_template ADD PRIMARY KEY (action_uuid);
SELECT partman.create_parent(
  'swoop.action',
  'created_at',
  'native',
  'monthly',
  p_template_table => 'swoop.action_template'
);


-- the noqa is here for GENERATED ALWAYS AS IDENTITY
-- https://github.com/sqlfluff/sqlfluff/issues/4455
CREATE TABLE IF NOT EXISTS swoop.thread ( -- noqa
  created_at timestamptz NOT NULL,
  last_update timestamptz NOT NULL,
  -- action_uuid reference to action omitted, we don't need referential integrity
  action_uuid uuid NOT NULL,
  status text NOT NULL REFERENCES swoop.event_state ON DELETE RESTRICT,
  next_attempt_after timestamptz,

  -- We lock with advisory locks that take two int4 values, one for the table
  -- OID and one for this lock_id. Note that this sequence can recycle values,
  -- but temporal locality means recycled values should not be temporaly conincident.
  -- Even if duplicates are "processable" at the same time, a lock ID conflict at worst
  -- causes added latency in processing, not skipped messages.
  --
  -- Recommended way to lock/unlock:
  --   pg_try_advisory_lock(to_regnamespace('thread')::oid, lock_id)
  --   pg_advisory_unlock(to_regnamespace('thread')::oid, lock_id)
  lock_id integer GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME swoop.thread_lock_id_seq
    MINVALUE -2147483648
    START WITH 1
    CYCLE
  )
) PARTITION BY RANGE (created_at);

CREATE INDEX ON swoop.thread (created_at);
CREATE INDEX ON swoop.thread (action_uuid);
CREATE INDEX ON swoop.thread (status);
CREATE TABLE IF NOT EXISTS swoop.thread_template (LIKE swoop.thread);
ALTER TABLE swoop.thread_template ADD PRIMARY KEY (action_uuid);
SELECT partman.create_parent(
  'swoop.thread',
  'created_at',
  'native',
  'monthly',
  p_template_table => 'swoop.thread_template'
);


CREATE TABLE IF NOT EXISTS swoop.event (
  event_time timestamptz NOT NULL,
  action_uuid uuid NOT NULL, -- reference omitted, we don't need referential integrity
  status text NOT NULL,
  -- max backoff cannot be more than 1 day (even that seems extreme in most cases)
  retry_seconds int CHECK (retry_seconds > 0 AND retry_seconds <= 86400),
  error text
) PARTITION BY RANGE (event_time);

CREATE INDEX ON swoop.event (event_time);
CREATE INDEX ON swoop.event (action_uuid);
CREATE TABLE IF NOT EXISTS swoop.event_template (LIKE swoop.event);
SELECT partman.create_parent(
  'swoop.event',
  'event_time',
  'native',
  'monthly',
  p_template_table => 'swoop.event_template'
);


CREATE OR REPLACE FUNCTION swoop.add_pending_event()
RETURNS trigger
LANGUAGE plpgsql VOLATILE
AS $$
DECLARE
BEGIN
  INSERT INTO swoop.event (event_time, action_uuid, status) VALUES
    (NEW.created_at, NEW.action_uuid, 'PENDING');
  RETURN NULL;
END;
$$;

CREATE OR REPLACE TRIGGER add_pending_event
AFTER INSERT ON swoop.action
FOR EACH ROW EXECUTE FUNCTION swoop.add_pending_event();


CREATE OR REPLACE FUNCTION swoop.update_thread()
RETURNS trigger
LANGUAGE plpgsql VOLATILE
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

CREATE OR REPLACE TRIGGER update_thread
AFTER INSERT ON swoop.event
FOR EACH ROW EXECUTE FUNCTION swoop.update_thread();


CREATE OR REPLACE VIEW swoop.action_thread AS
SELECT
  a.action_uuid AS action_uuid,
  a.action_type AS action_type,
  a.action_name AS action_name,
  a.parent_uuid AS parent_uuid,
  a.workflow_name AS workflow_name,
  a.created_at AS created_at,
  a.priority AS priority,
  t.last_update AS last_update,
  t.status AS status,
  t.next_attempt_after AS next_attempt_after,
  t.lock_id AS lock_id,
  (
    t.status = 'PENDING'
    OR t.status = 'BACKOFF' AND t.next_attempt_after <= now()
  ) AS is_processable
FROM
  swoop.thread AS t
  INNER JOIN swoop.action AS a USING (action_uuid);


CREATE OR REPLACE FUNCTION swoop.get_processable_actions(
  _limit smallint DEFAULT 10,
  _action_names text [] DEFAULT ARRAY[]::text []
)
RETURNS TABLE (action_uuid uuid, action_name text)
LANGUAGE plpgsql VOLATILE
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


CREATE OR REPLACE FUNCTION swoop.release_processable_lock(
  _action_uuid uuid
)
RETURNS bool
LANGUAGE plpgsql VOLATILE
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


-- migrate:down

DROP FUNCTION swoop.release_processable_lock;
DROP FUNCTION swoop.get_processable_actions;
DROP VIEW swoop.action_thread;
DROP TRIGGER update_thread ON swoop.event;
DROP FUNCTION swoop.update_thread;
DROP TRIGGER add_pending_event ON swoop.action;
DROP FUNCTION swoop.add_pending_event;
DROP TABLE swoop.event_template;
DROP TABLE swoop.event;
DROP TABLE swoop.thread_template;
DROP TABLE swoop.thread;
DROP TABLE swoop.action_template;
DROP TABLE swoop.action;
DROP TABLE swoop.event_state;
DROP EXTENSION pgtap;
DROP SCHEMA tap CASCADE;
DROP EXTENSION pg_partman;
DROP SCHEMA partman CASCADE;
DROP SCHEMA swoop CASCADE;
