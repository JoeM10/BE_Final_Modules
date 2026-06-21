import os
import unittest
from app import create_app
from app.models import Inventory, db
from app.utils.util import encode_token

os.environ.setdefault("PY_JOSE_TOKEN", "test-secret-key")

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.config["RATELIMIT_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.inventory_item1 = Inventory(
                item_name="Oil Filter",
                price=12.99
            )
            self.inventory_item2 = Inventory(
                item_name="Brake Pad",
                price=49.99
            )
            db.session.add_all([self.inventory_item1, self.inventory_item2])
            db.session.commit()
            self.inventory_item1_id = self.inventory_item1.id
            self.inventory_item2_id = self.inventory_item2.id

        self.admin_token = encode_token(user_id=0, role="admin")
        self.mechanic_token = encode_token(user_id=1, role="mechanic")

    def auth_header(self, token):
        return {"Authorization": "Bearer " + token}

    def test_create_inventory_item(self):
        inventory_payload = {
            "item_name": "Spark Plug",
            "price": 9.99
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["item_name"], "Spark Plug")
        self.assertEqual(response.json["price"], 9.99)

    def test_invalid_create_inventory_item(self):
        inventory_payload = {
            "item_name": "Spark Plug"
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["price"], ["Missing data for required field."])

    def test_get_all_inventory_items(self):
        response = self.client.get(
            "/inventory/",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["item_name"], "Oil Filter")
        self.assertEqual(response.json[1]["item_name"], "Brake Pad")

    def test_invalid_get_all_inventory_items(self):
        response = self.client.get("/inventory/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Token is missing!")

    def test_get_inventory_item(self):
        response = self.client.get(
            f"/inventory/{self.inventory_item1_id}",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], self.inventory_item1_id)
        self.assertEqual(response.json["item_name"], "Oil Filter")

    def test_invalid_get_inventory_item(self):
        response = self.client.get(
            "/inventory/999",
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Item not found")

    def test_update_inventory_item(self):
        update_payload = {
            "price": 15.99
        }

        response = self.client.put(
            f"/inventory/{self.inventory_item1_id}",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], self.inventory_item1_id)
        self.assertEqual(response.json["price"], 15.99)

    def test_invalid_update_inventory_item(self):
        update_payload = {
            "price": 15.99
        }

        response = self.client.put(
            "/inventory/999",
            json=update_payload,
            headers=self.auth_header(self.mechanic_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Item not found")

    def test_delete_inventory_item(self):
        response = self.client.delete(
            f"/inventory/{self.inventory_item2_id}",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["message"],
            f"Inventory item id: {self.inventory_item2_id}, deleted successfully."
        )

    def test_invalid_delete_inventory_item(self):
        response = self.client.delete(
            "/inventory/999",
            headers=self.auth_header(self.admin_token)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Service ticket not found")
