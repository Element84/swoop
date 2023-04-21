# SWOOP: STAC Workflow Open Orchestration Platform

## Pre-requisites<br>

Install [Dbmate](https://github.com/amacneil/dbmate), to create and manage database schema:
```
brew install dbmate
```
<br>

## Database Setup / Migrations

Instructions for this can be found in the Database README, found at:  `/db/README.md`

## Environment Setup and Testing

Refer to [Contributing.md](./CONTRIBUTING.md) for environment setup and testing instructions.

<br>

## Settings Management

Settings are managed using [Pydantic](https://docs.pydantic.dev/usage/settings/#dotenv-env-support)'s `BaseSettings` approach to creating and setting app specific configuration. Values can be loaded from:

- A dotenv file (or any file really as long as you tell the [Settings](./src/swoop/api/config.py) class which file to load).
- An explicit environment variable (e.g. `export DATABASE_NAME="foo"`).
- Both! The explicit environment variable will take precedence over the value in a dotenv file.

To get a settings object configured from a specific dotenv file:

```python
from swoop.api.config import get_settings
settings = Settings('.env')
```

If you don't provide an env file in `get_settings` swoop will default to (in this order):

- A `DOTENV` environment variable
- '.env'

<br><br><br>
This project is a work in progress.
