import os
import unittest
from datetime import date
from app import create_app
from app.models import Customer, Mechanic, Service_Ticket, db
from app.utils.util import encode_token

os.environ.setdefault("PY_JOSE_TOKEN", "test-secret-key")

class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.config["RATELIMIT_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.customer = Customer(
                name="test_customer",
                email="customer@email.com",
                phone="123-4567",
                password="test"
            )
            db.session.add(self.customer)
            db.session.commit()
            self.customer_id = self.customer.id

            self.mechanic1 = Mechanic(
                name="test_mechanic1",
                email="mechanic1@email.com",
                phone="222-3333",
                salary=50000,
                password="test"
            )
            db.session.add(self.mechanic1)
            db.session.commit()
            self.mechanic1_id = self.mechanic1.id

            self.mechanic2 = Mechanic(
                name="test_mechanic2",
                email="mechanic2@email.com",
                phone="222-4444",
                salary=55000,
                password="test"
            )
            db.session.add(self.mechanic2)
            db.session.commit()
            self.mechanic2_id = self.mechanic2.id

            self.service_ticket = Service_Ticket(
                VIN="1HGCM82633A004352",
                service_date=date(2026, 6, 18),
                service_desc="Oil change",
                customer_id=self.customer_id
            )
            self.service_ticket.mechanics.append(self.mechanic1)
            db.session.add(self.service_ticket)
            db.session.commit()

        self.admin_token = encode_token(user_id=0, role="admin")
        self.mechanic_token1 = encode_token(user_id=self.mechanic1_id, role="mechanic")

    def auth_header(self, token):
        return {"Authorization": "Bearer " + token}

    def test_login_mechanic(self):
        credentials = {
            "email": "mechanic1@email.com",
            "password": "test"
        }

        response = self.client.post("/mechanics/login", json=credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Mechanic test_mechanic1 logged in successfully")
        self.assertIn("token", response.json)

    def test_invalid_login_mechanic(self):
        credentials = {
            "email": "bad_mechanic@email.com",
            "password": "bad-password"
        }

        response = self.client.post("/mechanics/login", json=credentials)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid email or password.")

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Mechanic",
            "email": "johnmechanic@email.com",
            "phone": "333-4444",
            "salary": 60000,
            "password": "test"
        }

        response = self.client.post(
            "/mechanics/",
            json=mechanic_payload,
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Mechanic")
        self.assertEqual(response.json["email"], "johnmechanic@email.com")

    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            "name": "Duplicate Mechanic",
            "email": "mechanic1@email.com",
            "phone": "333-5555",
            "salary": 60000,
            "password": "test"
        }

        response = self.client.post(
            "/mechanics/",
            json=mechanic_payload,
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Mechanic with this email already exists")

    def test_get_all_mechanics(self):
        response = self.client.get(
            "/mechanics/",
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["email"], "mechanic1@email.com")
        self.assertEqual(response.json[1]["email"], "mechanic2@email.com")

    def test_invalid_get_all_mechanics(self):
        response = self.client.get("/mechanics/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_get_mechanic(self):
        response = self.client.get(
            f"/mechanics/{self.mechanic1_id}",
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], self.mechanic1_id)
        self.assertEqual(response.json["email"], "mechanic1@email.com")

    def test_invalid_get_mechanic(self):
        response = self.client.get(
            "/mechanics/999",
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Mechanic not found")

    def test_total_tickets(self):
        response = self.client.get(
            "/mechanics/total_tickets",
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["id"], self.mechanic1_id)
        self.assertEqual(len(response.json[0]["service_tickets"]), 1)

    def test_invalid_total_tickets(self):
        response = self.client.get("/mechanics/total_tickets")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_update_mechanic(self):
        update_payload = {
            "name": "Updated Mechanic",
            "salary": 65000
        }

        response = self.client.put(
            f"/mechanics/{self.mechanic1_id}",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Mechanic")
        self.assertEqual(response.json["salary"], 65000)

    def test_invalid_update_mechanic(self):
        update_payload = {
            "name": "Missing Mechanic"
        }

        response = self.client.put(
            "/mechanics/999",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token1)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Mechanic not found")

    def test_delete_mechanic(self):
        response = self.client.delete(
            f"/mechanics/{self.mechanic2_id}",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], f"Mechanic {self.mechanic2_id}, deleted successfully")

    def test_invalid_delete_mechanic(self):
        response = self.client.delete(
            "/mechanics/999",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Mechanic not found")
