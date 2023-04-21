from swoop.api.config import get_settings


def test_loads_from_env_file():
    """
    Simple test to verify we can load settings from an
    env file.
    """
    settings = get_settings(".env")
    assert settings.database_name == "swoop"
