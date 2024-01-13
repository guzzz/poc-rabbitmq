from structlog import get_logger

from config.db import mongoclient

log = get_logger()


class MessageRepository:

    def __init__(self):
        database = mongoclient.local
        self._messages = database.message

    def create(self, message):
        log.info("[DB] Registering MESSAGE...")
        return self._messages.insert_one(message)
