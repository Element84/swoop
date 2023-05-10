-- actions
INSERT INTO swoop.action VALUES (
  '2595f2da-81a6-423c-84db-935e6791046e',
  'workflow',
  'action_1',
  'handler_foo',
  5001,
  '2023-04-28 15:49:00+00',
  100
);
INSERT INTO swoop.action VALUES (
  '81842304-0aa9-4609-89f0-1c86819b0752',
  'workflow',
  'action_2',
  'handler_foo',
  5002,
  '2023-04-28 15:49:00+00',
  100
);

-- threads
--   created by action insert trigger

-- events
--     PENDING events created by action insert trigger
INSERT INTO swoop.event VALUES (
  '2023-04-28 15:49:01+00',
  '2595f2da-81a6-423c-84db-935e6791046e',
  'QUEUED',
  'swoop-db',
  300,
  'none'
);
INSERT INTO swoop.event VALUES (
  '2023-04-28 15:49:02+00',
  '2595f2da-81a6-423c-84db-935e6791046e',
  'RUNNING',
  'swoop-db',
  300,
  'none'
);
INSERT INTO swoop.event VALUES (
  '2023-04-28 15:49:03+00',
  '2595f2da-81a6-423c-84db-935e6791046e',
  'SUCCESSFUL',
  'swoop-db',
  300,
  'none'
);
