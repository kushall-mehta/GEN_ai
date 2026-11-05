import os
from pathlib import Path
import runpy
from unittest.mock import patch

from django.test import SimpleTestCase


class VercelSettingsTests(SimpleTestCase):
    def load_settings(self, **extra):
        environment = {
            "VERCEL": "1",
            "DJANGO_SECRET_KEY": "test-secret-for-settings-only",
            "DATABASE_URL": "postgresql://user:p%40ss@ep-example.neon.tech/gym?sslmode=require&channel_binding=require",
            "VERCEL_URL": "gym-preview.vercel.app",
        }
        environment.update(extra)
        with patch.dict(os.environ, environment, clear=True):
            return runpy.run_path(str(Path(__file__).with_name("settings.py")))

    def test_neon_url_and_deployment_hosts(self):
        settings = self.load_settings()
        database = settings["DATABASES"]["default"]
        self.assertEqual(database["PASSWORD"], "p@ss")
        self.assertEqual(database["CONN_MAX_AGE"], 0)
        self.assertEqual(database["OPTIONS"]["channel_binding"], "require")
        self.assertFalse(settings["DEBUG"])
        self.assertIn("gym-preview.vercel.app", settings["ALLOWED_HOSTS"])
        self.assertIn("https://gym-preview.vercel.app", settings["CSRF_TRUSTED_ORIGINS"])

    def test_vercel_rejects_ephemeral_sqlite(self):
        with self.assertRaisesRegex(RuntimeError, "SQLite is not persistent"):
            self.load_settings(DATABASE_URL="")
