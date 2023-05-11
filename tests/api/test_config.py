from swoop.api.config import Settings


def test_loads_from_env_file():
    """
    Simple test to verify we can load settings from an
    env file.
    """
    settings = Settings(".env")
    assert settings.db_name == "swoop"
