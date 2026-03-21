import pytest


def test_environment_is_working():
    """A simple sanity check to ensure pytest is running."""
    assert 1 + 1 == 2


@pytest.mark.django_db
def test_database_connection():
    """Ensure pytest can access the Django test database."""
    # We will expand this once we have models
    assert True
