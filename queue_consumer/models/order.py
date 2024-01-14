
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from config.postgresdb import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String)
    price = Column(MONEY)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    security_check = Column(Boolean, unique=False, default=True)
