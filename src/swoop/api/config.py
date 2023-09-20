from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self, *args, _env_file=None, **kwargs):
        if _env_file is not None:
            raise ValueError("swoop settings does not support loading an env file")
        super().__init__(*args, **kwargs)

    model_config = SettingsConfigDict(env_prefix="swoop_")

    # DATABASE HOST SETTINGS
    #
    # By default we use the libpq PGHOST var, but we will also use the
    # var SWOOP_DB_READER_HOST. This is to allow setting a different host
    # for reading than writing. The latter host can be set via the env var
    # SWOOP_DB_WRITER_HOST.
    #
    # Only the reader host is required to be set. If the writer host is
    # unspecified only one connection pool will be created, and it will be
    # shared for both reads and writes.
    db_reader_host: str | None = None
    db_writer_host: str | None = None

    # DATABASE NAME SETTING
    #
    # We use PGDATABASE for compatibility with libpq env vars.
    # The only reason we pull the setting in here is to allow
    # overriding during tests.
    db_name: str | None = Field(..., alias="PGDATABASE")

    db_min_conn_size: int = 2
    db_max_conn_size: int = 2
    db_max_queries: int = 50000
    db_max_inactive_conn_lifetime: float = 300

    bucket_name: str
    execution_dir: str
    s3_endpoint: str
    config_file: Path
