-- migrate:up

CREATE TABLE IF NOT EXISTS swoop.input_items (
  item_id text,
  collection text,
  PRIMARY KEY (item_id, collection)
);

CREATE TABLE IF NOT EXISTS swoop.payload_cache (
  payload_uuid uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  payload_hash bytea,
  workflow_version smallint,
  workflow_name text,
  created_at timestamptz NOT NULL DEFAULT now(),
  invalid_after timestamptz
);

CREATE INDEX ON swoop.payload_cache (payload_hash);

CREATE TABLE IF NOT EXISTS swoop.item_payload (
  item_id text NOT NULL,
  collection text NOT NULL,
  payload_uuid uuid NOT NULL REFERENCES swoop.payload_cache ON DELETE CASCADE,
  FOREIGN KEY (
    item_id,
    collection
  ) REFERENCES swoop.input_items ON DELETE RESTRICT,
  UNIQUE (item_id, collection, payload_uuid)
);

CREATE INDEX ON swoop.item_payload (item_id, collection);

ALTER TABLE swoop.action
ADD COLUMN payload_uuid uuid REFERENCES swoop.payload_cache ON DELETE RESTRICT;

ALTER TABLE swoop.action_template
ADD COLUMN payload_uuid uuid;


ALTER TABLE swoop.action
DROP CONSTRAINT workflow_or_callback;

ALTER TABLE swoop.action
ADD CONSTRAINT workflow_or_callback
CHECK (
  CASE
    WHEN
      action_type = 'callback'
      THEN
        parent_uuid IS NOT NULL
        AND payload_uuid IS NULL
    WHEN
      action_type = 'workflow' THEN
      action_name IS NOT NULL
      AND payload_uuid IS NOT NULL
  END
);


-- migrate:down

ALTER TABLE swoop.action
DROP CONSTRAINT workflow_or_callback;
ALTER TABLE swoop.action
ADD CONSTRAINT workflow_or_callback
CHECK (
  CASE
    WHEN
      action_type = 'callback'
      THEN
        parent_uuid IS NOT NULL
    WHEN
      action_type = 'workflow' THEN
      action_name IS NOT NULL
  END
);
ALTER TABLE swoop.action_template
DROP COLUMN payload_uuid;
ALTER TABLE swoop.action
DROP COLUMN payload_uuid;
DROP TABLE swoop.item_payload;
DROP TABLE swoop.payload_cache;
DROP TABLE swoop.input_items;
