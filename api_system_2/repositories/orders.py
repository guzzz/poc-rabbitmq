
from sqlalchemy.orm import Session
from structlog import get_logger

from api_system_2.models.order import Order
from api_system_2.config.database import get_db_session

log = get_logger()


class OrderRepository:

    def __init__(self):
        self.__db: Session = get_db_session()

    def list(self, last_id):
        log.info(f"[POSTGRESQL] Getting orders...")
        orders = self.__db.query(Order).offset(last_id).all()
        last_record = self.__db.query(Order).order_by(Order.id.desc()).first()
        if last_record:
            return orders, last_record.id
        else:
            return orders, 0
