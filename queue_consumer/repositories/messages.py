
import os
from structlog import get_logger
from config.mongodb import mongoclient

log = get_logger()
MONGO_EXPIRATION_SECONDS = float(os.getenv('MONGO_EXPIRATION_SECONDS'))


class MessageRepository:

    def __init__(self):
        database = mongoclient.local
        self.__messages = database.message
        self.__messages.create_index("processed_at", expireAfterSeconds=MONGO_EXPIRATION_SECONDS)

    def create(self, message):
        log.info("[MONGODB] Registering message...")
        return self.__messages.insert_one(message)
