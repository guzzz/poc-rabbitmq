import uuid
from sqlalchemy.orm import Session
from structlog import get_logger

from models.order import Order
from config.postgresdb import get_db_session

log = get_logger()


class OrderRepository:

    def __init__(self):
        self.__db: Session = get_db_session()

    def create(self, order: dict):
        log.info("[POSTGRESQL] Registering order...")
        db_order = Order(
            product=order.get("product"),
            price=order.get("price"),
        )
        self.__db.add(db_order)
        self.__db.commit()
        self.__db.refresh(db_order)
        return db_order
