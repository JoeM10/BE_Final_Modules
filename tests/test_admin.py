import os
import unittest
from app import create_app

os.environ.setdefault("PY_JOSE_TOKEN", "test-secret-key")

class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.admin_email = "admin@email.com"
        self.admin_password = "admin-password"
        os.environ["TEST_ADMIN_EMAIL"] = self.admin_email
        os.environ["TEST_ADMIN_PASSWORD"] = self.admin_password

        self.app = create_app("TestingConfig")
        self.app.config["RATELIMIT_ENABLED"] = False
        self.client = self.app.test_client()
    
    def test_login_admin(self):
        credentials = {
            "email": self.admin_email,
            "password": self.admin_password
        }

        response = self.client.post("/admin/login", json=credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Admin logged in successfully.")
        self.assertIn("token", response.json)

    def test_invalid_login_admin(self):
        credentials = {
            "email": "bad_admin@email.com",
            "password": "bad-password"
        }

        response = self.client.post("/admin/login", json=credentials)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid email or password.")
