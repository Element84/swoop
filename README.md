# SWOOP: STAC Workflow Open Orchestration Platform

## Pre-requisites<br>

Install [Dbmate](https://github.com/amacneil/dbmate), to create and manage database schema:
```
brew install dbmate
```
<br>


## Database Setup / Migrations

The DB schema and migrations are managed by [Dbmate](https://github.com/amacneil/dbmate#commands).

Existing migrations can be found in: `/db/migrations/`
<br><br>
### Database setup:

Create a `.env` file (specifying a `user`, `password`, `port`):
```
touch .env

echo "DATABASE_URL=\"postgres://{user}:{password}@127.0.0.1:{port}/swoop?sslmode=disable\"" >> .env2
```

Create the database and tables:
```
dbmate up
```



<br><br><br>
This project is a work in progress.