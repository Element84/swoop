# `swoop-db`

The swoop database schema is managed via `dbmate`. `dbmate` will apply all
migration files found in the `./migrations` directory and write the resulting
schema to `./schema.sql`. The latter action helps show what changes were made
by the applied migrations for verification purposes.

## Extensions

`swoop-db` makes use of two postgres extensions:

* `pg_partman`: an automated table partition manager
* `pgtap`: a postgres-native testing framework

## Database testing with docker

`./Dockerfile` defines the build steps for a database test container. The
container includes the requsite postgres extensions and any other required
utilities like `dbmate` and `pg_prove`. The root swoop-api `docker-compose.yml`
can be used to bring up the container with the necessary configuration, after
sourcing the root `.env` file to get the environment configuation.

The repo contents are mounted as `/swoop` inside the container to help
facilitate database operations and testing using the included utilities. For
example, to bring up the database and run the tests:

```shell
# bring up the database container in the background
docker compose up -d

# create the database and apply all migrations
docker compose exec postgres dbmate up

# run the database tests
docker compose exec postgres pg_prove -U postgres -d swoop --ext .sql db/tests/ -v

# connect to the database with psql
docker compose exec postgres psql -U postgres swoop
```

### Adding a migration

Use `dbmate` if needing to create a new migration file:

```shell
docker compose exec postgres dbmate new <migration_name>
```

### Adding database tests

Database tests should be added as `.sql` files in the `./tests` directory.
Follow the pattern of the existing test files. It's best to keep each file
short and focused with a descriptive name. For more about the `pgtap` test
framework see [the documentation](https://pgtap.org/documentation.html).

## pre-commit hooks related to the database

We use `sqlfluff` for linting sql. See the root `.sqlfluff` config file and the
command defined in the `.pre-commit-config.yaml` for more information. Note
that the tool is a bit slow and somewhat inaccurate at times; it is better than
nothing but we should not hesitate to replace it with a better option if one
becomes available.
