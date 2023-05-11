# SWOOP: STAC Workflow Open Orchestration Platform

This repo contains the database schema/migrations/tooling and API code for SWOOP.

This project is a work in progress. More information about this project and how
to use it will be coming as development progresses.

## Database Setup / Migrations

Instructions for this can be found in [the database `README.md`](./db/README.md)

## Environment Setup and Testing

Refer to [`CONTRIBUTING.md`](./CONTRIBUTING.md) for development setup and
testing instructions.

## Settings Management

All settings are managed via environment variables. See the API
[Settings](./src/swoop/api/config.py) class for SWOOP-specific settings. Many
database connection settings are specified via [libpq environment
variables](https://www.postgresql.org/docs/current/libpq-envars.html).

For testing purposes, one can source the [the `.env` file](./.env), which will
set all required env vars in the local shell environment.
