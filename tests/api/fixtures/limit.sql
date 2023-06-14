-- items
INSERT INTO swoop.input_item (item_uuid, item_id, collection) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fdd',
  'limitid1',
  'collection1'
);
INSERT INTO swoop.input_item (item_uuid, item_id, collection) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fde',
  'limitid2',
  'collection1'
);
INSERT INTO swoop.input_item (item_uuid, item_id, collection) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fdf',
  'limitid3',
  NULL
);


-- payloads
INSERT INTO swoop.payload_cache (
  payload_uuid,
  payload_hash,
  workflow_name,
  created_at
) VALUES (
  'b4918c13-477d-4553-85b2-9523f1fa5c51',
  decode('PsqWxdVjAjrV1+BueXnAS1cWIhU=', 'base64'),
  'some_workflow',
  '2023-04-28 15:49:00+00'
);

-- payloads
INSERT INTO swoop.payload_cache (
  payload_uuid,
  payload_hash,
  workflow_name,
  created_at
) VALUES (
  'aa152efa-db9f-4b8f-b96b-30621be68acd',
  decode('VsqWxdCjAjrX1+BueXnAS1cWIhU=', 'base64'),
  'other_workflow',
  '2023-05-28 15:49:00+00'
);

-- item - payload relations
INSERT INTO swoop.item_payload (item_uuid, payload_uuid) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fdd',
  'aa152efa-db9f-4b8f-b96b-30621be68acd'
);
INSERT INTO swoop.item_payload (item_uuid, payload_uuid) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fde',
  'aa152efa-db9f-4b8f-b96b-30621be68acd'
);
INSERT INTO swoop.item_payload (item_uuid, payload_uuid) VALUES (
  'c794de80-afb1-4379-87ce-ce0e60527fdf',
  'b4918c13-477d-4553-85b2-9523f1fa5c51'
);
