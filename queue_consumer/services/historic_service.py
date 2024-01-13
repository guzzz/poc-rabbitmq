import uuid
import json

from structlog import get_logger
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from repositories.message_repository import MessageRepository

message_repository = MessageRepository()
log = get_logger()


class HistoricService:

    def __init__(self):
        self.database = message_repository

    def save(self, message_in_bytes):
        log.info("[CREATE - message] Started creation message...")
        message_json = jsonable_encoder(message_in_bytes)
        message = json.loads(message_json)
        message['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        # message["id"] = uuid.uuid4()
        return self.database.create(message)
