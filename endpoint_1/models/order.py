
from sqlalchemy import Column, Integer, String

from endpoint_1.config.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    quantity = Column(Integer)
