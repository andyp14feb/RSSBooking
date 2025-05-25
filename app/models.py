from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Enum
import enum

Base = declarative_base()

class Therapist(Base):
    __tablename__ = "therapists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # "male" or "female"
    is_active = Column(Boolean, default=True)

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    price = Column(Float, nullable=False)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    therapist_id = Column(Integer, ForeignKey("therapists.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    date = Column(String, nullable=False)       # format: YYYY-MM-DD
    start_time = Column(String, nullable=False) # format: HH:MM
    end_time = Column(String, nullable=False)   # format: HH:MM


class RoleEnum(enum.Enum):
    admin = "admin"
    superadmin = "superadmin"

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
    role = Column(Enum(RoleEnum), default=RoleEnum.admin)
    is_active = Column(Boolean, default=True)
