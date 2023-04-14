BEGIN;

SET search_path = tap, public;
SELECT plan(3);

DO
$$
BEGIN
  FOR i in 1..300 LOOP
    INSERT INTO swoop.action (
      action_uuid,
      action_type,
      action_name,
      workflow_name,
      created_at
    ) VALUES (
      gen_random_uuid(),
      'workflow',
      'argo-workflow',
      'workflow-a',
      now()
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
  swoop.action_thread
WHERE
  is_processable;

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
    'should have exepcted number of locks on threads'
  )
FROM
  pg_locks
WHERE
  locktype = 'advisory'
  AND classid = to_regclass('swoop.thread')::oid;


SELECT * FROM finish(); -- noqa
ROLLBACK;
