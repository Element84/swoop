-- migrate:up

CREATE TABLE IF NOT EXISTS swoop.jobs(
  pk INT NOT NULL AUTO_INCREMENT,
  job_id UUID NOT NULL,
  payload json NOT NULL,
  
  PRIMARY KEY(pk),
  UNIQUE(job_id)
);

CREATE TABLE IF NOT EXISTS swoop.task_executions(
  pk INT NOT NULL AUTO_INCREMENT,
  task_id UUID NOT NULL,
  
  PRIMARY KEY(pk),
  UNIQUE(task_id)
);

CREATE TABLE IF NOT EXISTS swoop.workflows(
  pk INT NOT NULL AUTO_INCREMENT,
  workflow_id UUID NOT NULL,
  
  PRIMARY KEY(pk),
  UNIQUE(workflow_id)
);

-- migrate:down

DROP TABLE IF EXISTS swoop.jobs;

DROP TABLE IF EXISTS swoop.task_executions;

DROP TABLE IF EXISTS swoop.workflows;