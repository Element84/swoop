-- migrate:up

CREATE TABLE IF NOT EXISTS swoop.input_items (
    item_uuid uuid NOT NULL DEFAULT gen_random_uuid(),
    item_id text,
    collection text
);

CREATE INDEX ON swoop.input_items (item_uuid);


CREATE TABLE IF NOT EXISTS swoop.item_payload (
    item_uuid uuid NOT NULL,
    payload_uuid uuid NOT NULL
);

CREATE INDEX ON swoop.item_payload (item_uuid);
CREATE INDEX ON swoop.item_payload (payload_uuid);


CREATE TABLE IF NOT EXISTS swoop.payload_cache (
    cache_uuid uuid NOT NULL DEFAULT gen_random_uuid(),
    payload_uuid uuid NOT NULL gen_random_uuid(),
    cache_key text,
    workflow_version smallserial,
    workflow_name text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON swoop.payload_cache (cache_uuid);
CREATE INDEX ON swoop.payload_cache (payload_uuid);
CREATE INDEX ON swoop.payload_cache (created_at);


-- migrate:down

DROP TABLE swoop.input_items;
DROP TABLE swoop.item_payload;
DROP TABLE swoop.payload_cache;