# Mechanic Shop API

A Flask REST API for managing a mechanic shop database. The project uses Flask, SQLAlchemy, Marshmallow, and MySQL to handle customers, mechanics, and service tickets.

## Features

* Create, view, update, and delete customers
* Create, view, update, and delete mechanics
* Create, view, update, and delete service tickets
* MySQL database integration
* SQLAlchemy models and relationships
* Marshmallow schemas for serialization and validation
* Postman collection included for testing API routes

## Tech Stack

* Python
* Flask
* Flask-SQLAlchemy
* Marshmallow
* MySQL
* Postman

## Project Structure

This project is organized following the Application Factory Pattern.

```text
BE_Final_Modules/
├── app/
│   ├── blueprints/
│   │   ├── customers/
│   │   ├── mechanics/
│   │   └── service_tickets/
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
├── app.py
├── config.py
├── requirements.txt
├── Mechanic_Shop.postman_collection.json
└── README.md
```

## Database Models

### Customer

| Field   | Description            |
| ------- | ---------------------- |
| `id`    | Primary key            |
| `name`  | Customer name          |
| `email` | Customer email address |
| `phone` | Customer phone number  |

### Mechanic

| Field    | Description            |
| -------- | ---------------------- |
| `id`     | Primary key            |
| `name`   | Mechanic name          |
| `email`  | Mechanic email address |
| `phone`  | Mechanic phone number  |
| `salary` | Mechanic salary        |

### Service Ticket

| Field          | Description                                |
| -------------- | ------------------------------------------ |
| `id`           | Primary key                                |
| `VIN`          | Vehicle identification number              |
| `service_date` | Date of service                            |
| `service_desc` | Description of service needed or completed |
| `customer_id`  | Foreign key connected to the customer      |

## Relationships

* One customer can have many service tickets.
* One service ticket belongs to one customer.
* Service tickets and mechanics use a many-to-many relationship through an association table.

## Setup

Clone the repository:

```bash
git clone https://github.com/JoeM10/BE_Final_Modules.git
cd BE_Final_Modules
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the MySQL database:

```sql
CREATE DATABASE mechanic_shop_db;
```

Set your MySQL password as an environment variable:

```bash
set MYSQL_PASS=your_mysql_password
```

Run the app:

```bash
python app.py
```

The server will run at:

```text
http://127.0.0.1:5000
```

## API Routes

### Customers

| Method   | Endpoint          | Description                        |
| -------- | ----------------- | ---------------------------------- |
| `POST`   | `/customers/`     | Create a new customer              |
| `GET`    | `/customers/`     | Retrieve all customers             |
| `GET`    | `/customers/<id>` | Retrieve a specific customer by ID |
| `PUT`    | `/customers/<id>` | Update a specific customer by ID   |
| `DELETE` | `/customers/<id>` | Delete a specific customer by ID   |

### Mechanics

| Method   | Endpoint          | Description                        |
| -------- | ----------------- | ---------------------------------- |
| `POST`   | `/mechanics/`     | Create a new mechanic              |
| `GET`    | `/mechanics/`     | Retrieve all mechanics             |
| `GET`    | `/mechanics/<id>` | Retrieve a specific mechanic by ID |
| `PUT`    | `/mechanics/<id>` | Update a specific mechanic by ID   |
| `DELETE` | `/mechanics/<id>` | Delete a specific mechanic by ID   |

### Service Tickets

| Method   | Endpoint                                                     | Description                              |
| -------- | ------------------------------------------------------------ | ---------------------------------------- |
| `POST`   | `/service-tickets/`                                          | Create a new service ticket              |
| `GET`    | `/service-tickets/`                                          | Retrieve all service tickets             |
| `GET`    | `/service-tickets/<id>`                                      | Retrieve a specific service ticket by ID |
| `PUT`    | `/service-tickets/<id>`                                      | Update a specific service ticket by ID   |
| `DELETE` | `/service-tickets/<id>`                                      | Delete a specific service ticket by ID   |

## Testing

A Postman collection is included:

```text
Mechanic_Shop.postman_collection.json
```

Import this file into Postman to test the API endpoints.

## Author

Created by Joseph McDaniel
Github: https://github.com/JoeM10/