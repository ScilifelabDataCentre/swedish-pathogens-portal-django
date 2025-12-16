"""Test-specific settings for the SPP.

Set DJANGO_SETTINGS_MODULE (for pytest-django) to core.settings.testing.
These settings will be automatically used and no imports or overrides are needed.
"""

from .base import *  # noqa: F403

SECRET_KEY: str = "test-secret-key-not-for-production"

DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_db.sqlite3",
    }
}

ADMIN_URL: str = "admin/"

EMAIL_BACKEND: str = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL: str = "Pathogens Portal <no-reply@example.org>"
CONTACT_RECIPIENT_EMAIL: str = "dev-null@example.org"
EMAIL_TIMEOUT: int = 10
