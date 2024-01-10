import os

from redis import Redis
from structlog import get_logger

log = get_logger()

REDIS_EXPIRATION_TIME: int = os.getenv("REDIS_EXPIRATION_TIME")

class RedisService:

    def __init__(self):
        self.__redis_host = os.getenv("REDIS_HOST")
        self.__redis_port = os.getenv("REDIS_PORT")
        self.__redis = self.connect()

    def connect(self):
        try:
            return Redis(host=self.__redis_host, port=self.__redis_port, db=0)
        except Exception as exc:
            log.error(
                f"[ENDPOINT_1] Could not connect to Redis with "
                f"REDIS_HOST: {str(self.__redis_host)}" 
                f"REDIS_PORT: {str(self.__redis_port)}"
            )
            raise exc

    def get_value(self, key):
        log.info(f"[REDIS] Getting key: {key}")
        return self.__redis.get(key)

    def set_value(self, key, value):
        log.info(f"[REDIS] Setting key: {key}")
        # return self.__redis.set(key, value, ex=REDIS_EXPIRATION_TIME)
        return self.__redis.set(key, value)

    def delete_value(self, key):
        log.info(f"[REDIS] Deleting key: {key}")
        self.__redis.delete(key)
