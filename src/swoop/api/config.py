from functools import lru_cache
from pydantic import BaseSettings
import os
from urllib.parse import quote

default_env = os.getenv('DOTENV', '.env')

class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_user: str
    database_pass: str
    database_name: str
    database_url: str

    db_min_conn_size: int = 2
    db_max_conn_size: int = 2
    db_max_queries: int = 50000
    db_max_inactive_conn_lifetime: float = 300

    @property
    def reader_connection_string(self):
        """Create reader psql connection string."""
        return f"postgresql://{self.database_user}:{quote(self.database_pass)}@{self.database_host}:{self.database_port}/{self.database_name}"

    @property
    def writer_connection_string(self):
        """Create writer psql connection string."""
        return f"postgresql://{self.database_user}:{quote(self.database_pass)}@{self.database_host}:{self.database_port}/{self.database_name}"

    class Config():
        env_file = default_env

@lru_cache
def get_settings(*args, **kwargs):
    return Settings(*args, **kwargs)
