from pydantic import BaseSettings
import os

default_env = os.getenv("DOTENV", ".env")


class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_user: str
    database_pass: str
    database_name: str
    database_url: str

    class Config:
        env_file = default_env
