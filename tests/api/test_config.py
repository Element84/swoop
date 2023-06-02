import pytest

from swoop.api.config import Settings


def test_loads_from_env_vars():
    """
    Simple test to verify we can load settings from env.
    """
    settings = Settings()
    assert settings.db_name == "swoop"


def test_no_loads_from_env_file():
    """
    Simple test to verify we cannot load settings from an
    env file.
    """
    with pytest.raises(ValueError) as swoop_settings:
        Settings(_env_file=".env")
    assert (
        str(swoop_settings.value)
        == "swoop settings does not support loading an env file"
    )
