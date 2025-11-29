"""Basic smoke tests for initial project setup."""

from app.core.config import settings


def test_settings_loaded():
    assert settings.app.name == "Privacy Sandbox"

