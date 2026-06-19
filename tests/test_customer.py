import os
import unittest
from datetime import date
from app import create_app
from app.models import Customer, Service_Ticket, db
from app.utils.util import encode_token

os.environ.setdefault("PY_JOSE_TOKEN", "test-secret-key")

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.config["RATELIMIT_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.customer1 = Customer(
                name="test_user1",
                email="test1@email.com",
                phone="123-4567",
                password="test"
            )

            self.customer2 = Customer(
                name="test2_user",
                email="test2@email.com",
                phone="123-4562",
                password="test"
            )
            db.session.add_all([self.customer1, self.customer2])
            db.session.commit()
            self.customer2_id = self.customer2.id
            self.customer1_id = self.customer1.id

            self.service_ticket = Service_Ticket(
                VIN="1HGCM82633A004352",
                service_date=date(2026, 6, 18),
                service_desc="Oil change",
                customer_id=self.customer1_id
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            self.service_ticket_id = self.service_ticket.id

        self.customer_token1 = encode_token(user_id=self.customer1_id, role="customer")
        self.customer_token2 = encode_token(user_id=self.customer2_id, role="customer")
        self.admin_token = encode_token(user_id=0, role="admin")

    def auth_header(self, token):
        return {"Authorization": "Bearer " + token}

    def test_login_customer(self):
        credentials = {
            "email": "test1@email.com",
            "password": "test"
        }

        response = self.client.post("/customers/login", json=credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertIn("token", response.json)

    def test_invalid_login_customer(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post("/customers/login", json=credentials)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Invalid email or password!")

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "333-6666",
            "password": "123"
        }

        response = self.client.post("/customers/", json=customer_payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")
        self.assertEqual(response.json["email"], "jd@email.com")

    def test_invalid_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "123-456-7890",
            "password": "123"
        }

        response = self.client.post("/customers/", json=customer_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["email"], ["Missing data for required field."])

    def test_get_my_tickets(self):
        response = self.client.get(
            "/customers/my-tickets",
            headers=self.auth_header(self.customer_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["customer_id"], self.customer1_id)

    def test_invalid_get_my_tickets(self):
        missing_customer_token = encode_token(user_id=999, role="customer")

        response = self.client.get(
            "/customers/my-tickets",
            headers=self.auth_header(missing_customer_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Customer not found.")

    def test_get_all_customers(self):
        response = self.client.get(
            "/customers/",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["email"], "test1@email.com")
        self.assertEqual(response.json[1]["email"], "test2@email.com")

    def test_invalid_get_all_customers(self):
        response = self.client.get("/customers/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_get_customer(self):
        response = self.client.get(
            f"/customers/{self.customer1_id}",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], self.customer1_id)
        self.assertEqual(response.json["email"], "test1@email.com")

    def test_invalid_get_customer(self):
        response = self.client.get(
            "/customers/999",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Customer not found.")

    def test_update_customer(self):
        update_payload = {
            "name": "Peter",
            "phone": "111-3456",
            "email": "test@email.com",
            "password": "1234"
        }

        response = self.client.put(
            "/customers/update_account",
            json=update_payload,
            headers=self.auth_header(self.customer_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Peter")
        self.assertEqual(response.json["email"], "test@email.com")

    def test_invalid_update_customer(self):
        update_payload = {
            "name": "Peter",
            "phone": "111-3456",
            "email": "",
            "password": "123"
        }

        response = self.client.put(
            "/customers/update_account",
            json=update_payload,
            headers=self.auth_header(self.customer_token1)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["email"],
            ["Not a valid email address.", "Field cannot be blank."]
        )

    def test_admin_update_customer(self):
        update_payload = {
            "name": "Admin Updated",
            "phone": "999-8888"
        }

        response = self.client.put(
            f"/customers/{self.customer1_id}",
            json=update_payload,
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Admin Updated")
        self.assertEqual(response.json["phone"], "999-8888")

    def test_invalid_admin_update_customer(self):
        update_payload = {
            "name": "Admin Updated",
            "phone": ""
        }

        response = self.client.put(
            f"/customers/{self.customer1_id}",
            json=update_payload,
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["phone"], ["Field cannot be blank."])

    def test_delete_current_customer(self):
        response = self.client.delete(
            "/customers/delete_account",
            headers=self.auth_header(self.customer_token2)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["message"],
            f"Customer {self.customer2_id} deleted successfully."
        )

    def test_invalid_delete_current_customer(self):
        missing_customer_token = encode_token(user_id=999, role="customer")

        response = self.client.delete(
            "/customers/delete_account",
            headers=self.auth_header(missing_customer_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Customer not found.")

    def test_admin_delete_customer(self):
        response = self.client.delete(
            f"/customers/{self.customer2_id}",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Customer deleted successfully.")

    def test_invalid_admin_delete_customer(self):
        response = self.client.delete(
            "/customers/999",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Customer not found.")
