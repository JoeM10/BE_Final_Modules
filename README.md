# Mechanic Shop API

A Flask REST API (Application Programming Interface) for managing a mechanic shop database. This project supports customers, mechanics, service tickets, inventory parts, parts used on tickets, token authentication, role-based route protection, rate limiting, caching, Swagger API documentation, automated unit tests, and Postman testing.

## Features

| Feature                   | Description                                                                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Customer management       | Create customers, log in as a customer, view customer records, update accounts, delete accounts, and view a customer's own service tickets. |
| Mechanic management       | Create, view, update, and delete mechanics, log in as a mechanic, and view mechanics sorted by total service tickets worked on.             |
| Service ticket management | Create, view, update, and delete service tickets for customer vehicles.                                                                     |
| Mechanic assignment       | Add mechanics to service tickets and remove mechanics from service tickets.                                                                 |
| Inventory management      | Create, view, update, and delete inventory parts used by the mechanic shop.                                                                 |
| Parts per ticket          | Add parts to service tickets, update part quantities, and remove parts from service tickets.                                                |
| Token authentication      | Uses JWT (JSON Web Token) authentication with role data for customers, mechanics, and admins.                                               |
| Role-based protection     | Protects routes using customer, mechanic, and admin roles.                                                                                  |
| Rate limiting             | Uses Flask-Limiter to limit requests on selected routes.                                                                                    |
| Caching                   | Uses Flask-Caching with SimpleCache configuration.                                                                                          |
| Swagger documentation     | Includes Swagger UI documentation for viewing and testing API routes in the browser.                                                        |
| Automated testing         | Includes Python unit tests for admin, customer, mechanic, inventory, and service ticket routes.                                             |
| Postman testing           | Includes a Postman collection for testing API routes.                                                                                       |

## Tech Stack

| Technology             | Purpose                                                                       |
| ---------------------- | ----------------------------------------------------------------------------- |
| Python                 | Main programming language.                                                    |
| Flask                  | Web framework used to build the API.                                          |
| Flask-SQLAlchemy       | ORM (Object Relational Mapper) used to connect Python models to MySQL tables. |
| SQLAlchemy             | Database modeling and query support.                                          |
| MySQL                  | Relational database used by the project.                                      |
| mysql-connector-python | MySQL database driver.                                                        |
| Marshmallow            | Request validation and response serialization.                                |
| Flask-Marshmallow      | Flask integration for Marshmallow schemas.                                    |
| python-jose            | JWT (JSON Web Token) creation and validation.                                 |
| Flask-Limiter          | API route rate limiting.                                                      |
| Flask-Caching          | Route and app-level caching support.                                          |
| Flask-Swagger          | Swagger documentation support.                                                |
| Flask-Swagger-UI       | Browser-based Swagger UI for API documentation.                               |
| unittest               | Python testing framework used for automated route tests.                      |
| Postman                | API testing through the included collection.                                  |

## Project Structure

```text
BE_Final_Modules/
├── app/
│   ├── blueprints/
│   │   ├── admin/
│   │   ├── customers/
│   │   ├── inventory/
│   │   ├── mechanics/
│   │   └── service_tickets/
│   ├── static/
│   │   └── swagger.yaml
│   ├── utils/
│   │   └── util.py
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
├── tests/
│   ├── test_admin.py
│   ├── test_customer.py
│   ├── test_inventory.py
│   ├── test_mechanics.py
│   └── test_service_tickets.py
├── app.py
├── config.py
├── example_data.txt
├── Mechanic_Shop.postman_collection.json
├── requirements.txt
└── README.md
```

## Database Models

### Customer

| Field      | Type    | Constraints      | Description                |
| ---------- | ------- | ---------------- | -------------------------- |
| `id`       | Integer | Primary key      | Unique customer ID.        |
| `name`     | String  | Required         | Customer name.             |
| `email`    | String  | Required, unique | Customer email address.    |
| `phone`    | String  | Required, unique | Customer phone number.     |
| `password` | String  | Required         | Customer account password. |

### Mechanic

| Field      | Type    | Constraints      | Description                |
| ---------- | ------- | ---------------- | -------------------------- |
| `id`       | Integer | Primary key      | Unique mechanic ID.        |
| `name`     | String  | Required         | Mechanic name.             |
| `email`    | String  | Required, unique | Mechanic email address.    |
| `phone`    | String  | Required, unique | Mechanic phone number.     |
| `salary`   | Float   | Required         | Mechanic salary.           |
| `password` | String  | Required         | Mechanic account password. |

### Service_Ticket

| Field          | Type    | Constraints           | Description                                 |
| -------------- | ------- | --------------------- | ------------------------------------------- |
| `id`           | Integer | Primary key           | Unique service ticket ID.                   |
| `VIN`          | String  | Required              | VIN (Vehicle Identification Number).        |
| `service_date` | Date    | Required              | Date of service.                            |
| `service_desc` | String  | Required              | Description of service needed or completed. |
| `customer_id`  | Integer | Foreign key, required | ID of the customer connected to the ticket. |

### Inventory

| Field       | Type    | Constraints      | Description                  |
| ----------- | ------- | ---------------- | ---------------------------- |
| `id`        | Integer | Primary key      | Unique inventory item ID.    |
| `item_name` | String  | Required, unique | Name of the part or item.    |
| `price`     | Float   | Required         | Price of the inventory item. |

### Parts_Per_Ticket

| Field           | Type    | Constraints              | Description                                      |
| --------------- | ------- | ------------------------ | ------------------------------------------------ |
| `id`            | Integer | Primary key              | Unique parts-per-ticket record ID.               |
| `part_id`       | Integer | Foreign key, required    | ID of the inventory part.                        |
| `ticket_id`     | Integer | Foreign key, required    | ID of the service ticket.                        |
| `part_quantity` | Integer | Required, greater than 0 | Quantity of the part used on the service ticket. |

## Database Relationships

| Relationship                      | Type         | Description                                                                                |
| --------------------------------- | ------------ | ------------------------------------------------------------------------------------------ |
| Customer → Service_Ticket         | One-to-many  | One customer can have many service tickets.                                                |
| Service_Ticket → Customer         | Many-to-one  | Each service ticket belongs to one customer.                                               |
| Service_Ticket ↔ Mechanic         | Many-to-many | A service ticket can have many mechanics, and a mechanic can work on many service tickets. |
| Service_Ticket → Parts_Per_Ticket | One-to-many  | A service ticket can have many parts assigned to it.                                       |
| Inventory → Parts_Per_Ticket      | One-to-many  | One inventory item can be used on many service tickets.                                    |

## Setup

Clone the repository:

```bash
git clone https://github.com/JoeM10/BE_Final_Modules.git
cd BE_Final_Modules
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the MySQL database:

```sql
CREATE DATABASE mechanic_shop_db;
```

Set environment variables:

| Variable              | Description                              |
| --------------------- | ---------------------------------------- |
| `MYSQL_PASS`          | MySQL password used in the database URI. |
| `PY_JOSE_TOKEN`       | Secret key used for JWT tokens.          |
| `TEST_ADMIN_EMAIL`    | Admin login email.                       |
| `TEST_ADMIN_PASSWORD` | Admin login password.                    |

Run the app:

```bash
python app.py
```

Server URL:

```text
http://127.0.0.1:5000
```

## Swagger API Documentation

Swagger UI has been added to provide browser-based documentation for the API routes.

After starting the Flask app, open the Swagger documentation at:

```text
http://127.0.0.1:5000/api/docs
```

The Swagger UI uses the `swagger.yaml` file located in:

```text
app/static/swagger.yaml
```

This allows the API routes, request bodies, response examples, and authentication requirements to be documented in one place.

## API Routes

### Admin Routes

| Method | Endpoint       | Auth Required | Description                             |
| ------ | -------------- | ------------- | --------------------------------------- |
| `POST` | `/admin/login` | No            | Log in as an admin and receive a token. |

### Customer Routes

| Method   | Endpoint                    | Auth Required     | Description                                         |
| -------- | --------------------------- | ----------------- | --------------------------------------------------- |
| `POST`   | `/customers/`               | No                | Create a new customer.                              |
| `POST`   | `/customers/login`          | No                | Log in as a customer and receive a token.           |
| `GET`    | `/customers/my-tickets`     | Customer          | Get all service tickets for the logged-in customer. |
| `GET`    | `/customers/`               | Mechanic or Admin | Get all customers.                                  |
| `GET`    | `/customers/<int:id>`       | Mechanic or Admin | Get one customer by ID.                             |
| `PUT`    | `/customers/update_account` | Customer          | Update the logged-in customer's account.            |
| `PUT`    | `/customers/<int:id>`       | Mechanic or Admin | Update a customer by ID.                            |
| `DELETE` | `/customers/delete_account` | Customer          | Delete the logged-in customer's account.            |
| `DELETE` | `/customers/<int:id>`       | Mechanic or Admin | Delete a customer by ID.                            |

### Mechanic Routes

| Method   | Endpoint                   | Auth Required     | Description                                             |
| -------- | -------------------------- | ----------------- | ------------------------------------------------------- |
| `POST`   | `/mechanics/login`         | No                | Log in as a mechanic and receive a token.               |
| `POST`   | `/mechanics/`              | Admin             | Create a new mechanic.                                  |
| `GET`    | `/mechanics/`              | Mechanic or Admin | Get all mechanics.                                      |
| `GET`    | `/mechanics/<int:id>`      | Mechanic or Admin | Get one mechanic by ID.                                 |
| `GET`    | `/mechanics/total_tickets` | Mechanic or Admin | Get mechanics sorted by total assigned service tickets. |
| `PUT`    | `/mechanics/<int:id>`      | Mechanic or Admin | Update a mechanic by ID.                                |
| `DELETE` | `/mechanics/<int:id>`      | Admin             | Delete a mechanic by ID.                                |

### Service Ticket Routes

| Method   | Endpoint                                               | Auth Required     | Description                                                 |
| -------- | ------------------------------------------------------ | ----------------- | ----------------------------------------------------------- |
| `POST`   | `/service-tickets/`                                    | Mechanic or Admin | Create a new service ticket.                                |
| `GET`    | `/service-tickets/`                                    | Mechanic or Admin | Get all service tickets.                                    |
| `GET`    | `/service-tickets/<int:id>`                            | Mechanic or Admin | Get one service ticket by ID.                               |
| `PUT`    | `/service-tickets/<int:id>/edit`                       | Mechanic or Admin | Add or remove mechanics assigned to a service ticket.       |
| `POST`   | `/service-tickets/<int:ticket_id>/parts`               | Mechanic or Admin | Add an inventory part to a service ticket.                  |
| `PUT`    | `/service-tickets/<int:ticket_id>/parts/<int:part_id>` | Mechanic or Admin | Update the quantity of a part assigned to a service ticket. |
| `DELETE` | `/service-tickets/<int:ticket_id>/parts/<int:part_id>` | Mechanic or Admin | Remove a part from a service ticket.                        |
| `DELETE` | `/service-tickets/<int:id>`                            | Mechanic or Admin | Delete a service ticket by ID.                              |

### Inventory Routes

| Method   | Endpoint              | Auth Required     | Description                     |
| -------- | --------------------- | ----------------- | ------------------------------- |
| `POST`   | `/inventory/`         | Mechanic or Admin | Create a new inventory item.    |
| `GET`    | `/inventory/`         | Mechanic or Admin | Get all inventory items.        |
| `GET`    | `/inventory/<int:id>` | Mechanic or Admin | Get one inventory item by ID.   |
| `PUT`    | `/inventory/<int:id>` | Mechanic or Admin | Update an inventory item by ID. |
| `DELETE` | `/inventory/<int:id>` | Mechanic or Admin | Delete an inventory item by ID. |

## Example Request Data

See `example_data.txt` for example request data.

## Testing

### Automated Unit Tests

Automated unit tests have been added in the `tests/` folder. These tests use Python's `unittest` framework and Flask's test client to check expected API behavior.

The test files include:

```text
tests/test_admin.py
tests/test_customer.py
tests/test_inventory.py
tests/test_mechanics.py
tests/test_service_tickets.py
```

The tests cover successful and unsuccessful route behavior for admin login, customer routes, mechanic routes, inventory routes, service ticket routes, authentication requirements, and validation errors.

To run the automated tests:

```bash
python -m unittest discover -s tests
```

### Postman Testing

A Postman collection is included:

```text
Mechanic_Shop.postman_collection.json
```

Import this file into Postman to test the API endpoints manually.

## Author

Created by Joseph McDaniel
GitHub: https://github.com/JoeM10/
