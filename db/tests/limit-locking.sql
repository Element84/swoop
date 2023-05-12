BEGIN;

SET search_path = tap, public;
SELECT plan(3);

INSERT INTO swoop.payload_cache (
  payload_uuid,
  payload_hash,
  workflow_version,
  workflow_name,
  created_at,
  invalid_after
) VALUES (
  'cdc73916-500c-4501-a658-dd706a943d19'::uuid,
  decode('123\000456', 'escape'),
  1,
  'workflow-a',
  '2023-04-14 00:25:07.388012+00'::timestamptz,
  '2023-04-20 00:25:07.388012+00'::timestamptz
);

DO
$$
BEGIN
  FOR i in 1..300 LOOP
    INSERT INTO swoop.action (
      action_uuid,
      action_type,
      handler_name,
      action_name,
      created_at,
      payload_uuid
    ) VALUES (
      gen_random_uuid(),
      'workflow',
      'argo-workflow',
      'workflow-a',
      now(),
      'cdc73916-500c-4501-a658-dd706a943d19'::uuid
    );
  END LOOP;
END;
$$;

SELECT
  is(
    count(*),
    300::bigint,
    'should have expected number of processable threads'
  )
FROM
  swoop.thread AS t --noqa: AL05
WHERE
  swoop.thread_is_processable(t);

SELECT
  is(
    count(*),
    10::bigint,
    'should get expected number of processable actions'
  )
FROM
  swoop.get_processable_actions(
    _ignored_action_uuids => ARRAY[]::uuid []
  );

SELECT
  is(
    count(*),
    10::bigint,
    'should have expected number of locks on threads'
  )
FROM
  pg_locks
WHERE
  locktype = 'advisory'
  AND classid = to_regclass('swoop.thread')::oid;


SELECT * FROM finish(); -- noqa
ROLLBACK;
