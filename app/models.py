from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True)
)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False, unique=True,)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    tickets: Mapped[List["Service_Ticket"]] = db.relationship(back_populates="customer")

class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(nullable=False)

    service_tickets: Mapped[List["Service_Ticket"]] = db.relationship(secondary=service_mechanics, back_populates="mechanics")

class Service_Ticket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(50), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates="tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanics, back_populates="service_tickets")