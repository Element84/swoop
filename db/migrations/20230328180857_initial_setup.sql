-- migrate:up

CREATE TABLE IF NOT EXISTS jobs(
  pk SERIAL PRIMARY KEY,
  job_id UUID UNIQUE NOT NULL,
  payload json NOT NULL
);

CREATE TABLE IF NOT EXISTS task_executions(
  pk SERIAL PRIMARY KEY,
  task_id UUID UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS workflows(
  pk SERIAL PRIMARY KEY,
  workflow_id UUID UNIQUE NOT NULL
);

-- migrate:down

DROP TABLE IF EXISTS jobs;

DROP TABLE IF EXISTS task_executions;

DROP TABLE IF EXISTS workflows;
