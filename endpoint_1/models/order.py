
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy import Column, Integer, String

from app.config.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    quantity = Column(Integer)
    price = Column(MONEY)
