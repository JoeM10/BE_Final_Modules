import os
import unittest
from datetime import date
from app import create_app
from app.models import Customer, Inventory, Mechanic, Parts_Per_Ticket, Service_Ticket, db
from app.utils.util import encode_token

os.environ.setdefault("PY_JOSE_TOKEN", "test-secret-key")

class TestServiceTickets(unittest.TestCase):
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
            self.mechanic2 = Mechanic(
                name="test_mechanic2",
                email="mechanic2@email.com",
                phone="222-4444",
                salary=55000,
                password="test"
            )
            db.session.add_all([self.mechanic1, self.mechanic2])
            db.session.commit()
            self.mechanic1_id = self.mechanic1.id
            self.mechanic2_id = self.mechanic2.id

            self.part1 = Inventory(
                item_name="Oil Filter",
                price=12.99
            )
            self.part2 = Inventory(
                item_name="Brake Pad",
                price=49.99
            )
            db.session.add_all([self.part1, self.part2])
            db.session.commit()
            self.part1_id = self.part1.id
            self.part2_id = self.part2.id

            self.service_ticket1 = Service_Ticket(
                VIN="1HGCM82633A004352",
                service_date=date(2026, 6, 18),
                service_desc="Oil change",
                customer_id=self.customer_id
            )
            self.service_ticket1.mechanics.append(self.mechanic1)
            self.service_ticket2 = Service_Ticket(
                VIN="1HGCM82633A004353",
                service_date=date(2026, 6, 19),
                service_desc="Brake inspection",
                customer_id=self.customer_id
            )
            db.session.add_all([self.service_ticket1, self.service_ticket2])
            db.session.commit()
            self.service_ticket1_id = self.service_ticket1.id
            self.service_ticket2_id = self.service_ticket2.id

            self.ticket_part = Parts_Per_Ticket(
                ticket_id=self.service_ticket1_id,
                part_id=self.part1_id,
                part_quantity=1
            )
            db.session.add(self.ticket_part)
            db.session.commit()

        self.admin_token = encode_token(user_id=0, role="admin")
        self.mechanic_token = encode_token(user_id=self.mechanic1_id, role="mechanic")

    def auth_header(self, token):
        return {"Authorization": "Bearer " + token}

    def test_create_service_ticket(self):
        service_ticket_payload = {
            "VIN": "1HGCM82633A004354",
            "service_date": "2026-06-20",
            "service_desc": "Tire rotation",
            "customer_id": self.customer_id
        }

        response = self.client.post(
            "/service-tickets/",
            json=service_ticket_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["VIN"], "1HGCM82633A004354")
        self.assertEqual(response.json["customer_id"], self.customer_id)

    def test_invalid_create_service_ticket(self):
        service_ticket_payload = {
            "VIN": "1HGCM82633A004354",
            "service_date": "2026-06-20",
            "service_desc": "Tire rotation",
            "customer_id": 999
        }

        response = self.client.post(
            "/service-tickets/",
            json=service_ticket_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Customer not found.")

    def test_get_all_service_tickets(self):
        response = self.client.get(
            "/service-tickets/",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["customer_id"], self.customer_id)

    def test_invalid_get_all_service_tickets(self):
        response = self.client.get("/service-tickets/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_get_service_ticket(self):
        response = self.client.get(
            f"/service-tickets/{self.service_ticket1_id}",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], self.service_ticket1_id)
        self.assertEqual(response.json["VIN"], "1HGCM82633A004352")

    def test_invalid_get_service_ticket(self):
        response = self.client.get(
            "/service-tickets/999",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found")

    def test_update_service_ticket(self):
        update_payload = {
            "add_mechanic_ids": [self.mechanic2_id],
            "remove_mechanic_ids": [self.mechanic1_id]
        }

        response = self.client.put(
            f"/service-tickets/{self.service_ticket1_id}/edit",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["mechanics"]), 1)
        self.assertEqual(response.json["mechanics"][0]["id"], self.mechanic2_id)

    def test_invalid_update_service_ticket(self):
        update_payload = {
            "add_mechanic_ids": [self.mechanic2_id],
            "remove_mechanic_ids": []
        }

        response = self.client.put(
            "/service-tickets/999/edit",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found")

    def test_add_part_to_ticket(self):
        part_payload = {
            "part_id": self.part2_id,
            "part_quantity": 2
        }

        response = self.client.post(
            f"/service-tickets/{self.service_ticket1_id}/parts",
            json=part_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["parts_used"]), 2)

    def test_invalid_add_part_to_ticket(self):
        part_payload = {
            "part_id": self.part2_id,
            "part_quantity": 0
        }

        response = self.client.post(
            f"/service-tickets/{self.service_ticket1_id}/parts",
            json=part_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "part_quantity must be greater than 0.")

    def test_update_ticket_part_quantity(self):
        update_payload = {
            "part_quantity": 3
        }

        response = self.client.put(
            f"/service-tickets/{self.service_ticket1_id}/parts/{self.part1_id}",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["parts_used"][0]["part_quantity"], 3)

    def test_invalid_update_ticket_part_quantity(self):
        update_payload = {
            "part_quantity": 3
        }

        response = self.client.put(
            f"/service-tickets/{self.service_ticket2_id}/parts/{self.part1_id}",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Part is not assigned to this service ticket.")

    def test_remove_part_from_ticket(self):
        response = self.client.delete(
            f"/service-tickets/{self.service_ticket1_id}/parts/{self.part1_id}",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["parts_used"], [])

    def test_invalid_remove_part_from_ticket(self):
        response = self.client.delete(
            f"/service-tickets/{self.service_ticket2_id}/parts/{self.part1_id}",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Part is not assigned to this service ticket.")

    def test_delete_service_ticket(self):
        response = self.client.delete(
            f"/service-tickets/{self.service_ticket2_id}",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["message"],
            f"Service ticket id: {self.service_ticket2_id}, deleted successfully."
        )

    def test_invalid_delete_service_ticket(self):
        response = self.client.delete(
            "/service-tickets/999",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found")
