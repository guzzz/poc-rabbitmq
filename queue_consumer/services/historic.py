import json

from fastapi.encoders import jsonable_encoder
from datetime import datetime

from repositories.messages import MessageRepository


class HistoricService:

    def __init__(self):
        self.database = MessageRepository()

    def save(self, message_in_bytes):
        message_json = jsonable_encoder(message_in_bytes)
        message = json.loads(message_json)
        message['processed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return self.database.create(message)
