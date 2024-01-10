import uuid
from sqlalchemy.orm import Session
from structlog import get_logger

from app.models.order import Order
from datetime import datetime

log = get_logger()


class OrderRepository:

    def __init__(self):
        pass

    def list(self, db: Session, start_id):
        log.info(f"[DB] Listing ORDER.")
        return db.query(Order).offset(start_id).all()
