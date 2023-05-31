-- items
INSERT INTO swoop.input_item VALUES (
  'id1',
  'collection1'
);
INSERT INTO swoop.input_item VALUES (
  'id2',
  'collection1'
);
INSERT INTO swoop.input_item VALUES (
  'id3',
  'collection2'
);
INSERT INTO swoop.input_item VALUES (
  'id4',
  'collection2'
);

-- payloads
INSERT INTO swoop.payload_cache VALUES (
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77',
  decode('PsqWxdKjAjrV1+BueXnAS1cWIhU=', 'base64'),
  1,
  'some_workflow',
  '2023-04-28 15:49:00+00',
  null
);

-- item - payload relations
INSERT INTO swoop.item_payload VALUES (
  'id1',
  'collection1',
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
);

INSERT INTO swoop.item_payload VALUES (
  'id2',
  'collection1',
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
);

INSERT INTO swoop.item_payload VALUES (
  'id3',
  'collection2',
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
);

INSERT INTO swoop.item_payload VALUES (
  'id4',
  'collection2',
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
);

-- actions
INSERT INTO swoop.action VALUES (
  '2595f2da-81a6-423c-84db-935e6791046e',
  'workflow',
  'action_1',
  'handler_foo',
  'cf8ff7f0-ce5d-4de6-8026-4e551787385f',
  '2023-04-28 15:49:00+00',
  100,
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
);
INSERT INTO swoop.action VALUES (
  '81842304-0aa9-4609-89f0-1c86819b0752',
  'workflow',
  'action_2',
  'handler_foo',
  '2595f2da-81a6-423c-84db-935e6791046e',
  '2023-04-28 15:49:00+00',
  100,
  'ade69fe7-1d7d-472e-9f36-7242cc2aca77'
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
