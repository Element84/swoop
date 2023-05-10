from pydantic import BaseSettings
import os
from urllib.parse import quote

default_env = os.getenv("DOTENV", ".env")


class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_user: str
    database_pass: str
    database_name: str
    database_url_extra: str = ""
    database_url: str | None=None

    db_min_conn_size: int = 2
    db_max_conn_size: int = 2
    db_max_queries: int = 50000
    db_max_inactive_conn_lifetime: float = 300

    def build_db_connection_string(self, **kwargs):
        """Build a DB connection string from setttings, with optional overrides"""
        ctx = {
            "host": self.database_host,
            "port": self.database_port,
            "user": self.database_user,
            "password": self.database_pass,
            "name": self.database_name,
            "url_extra": self.database_url_extra,
        }
        ctx.update(kwargs)
        return (
            f"postgresql://{ctx['user']}:{quote(ctx['password'])}"
            f"@{ctx['host']}:{ctx['port']}/{ctx['name']}{ctx['url_extra']}"
        )

    @property
    def reader_connection_string(self):
        """Create reader psql connection string."""
        if self.database_url:
            return self.database_url
        return self.build_db_connection_string()

    @property
    def writer_connection_string(self):
        """Create writer psql connection string."""
        if self.database_url:
            return self.database_url
        return self.build_db_connection_string()

    class Config:
        env_file = default_env
