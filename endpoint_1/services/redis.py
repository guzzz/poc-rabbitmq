import os
import json

from redis import Redis
from structlog import get_logger
from datetime import datetime

log = get_logger()

REDIS_EXPIRATION_TIME: int = os.getenv("REDIS_EXPIRATION_TIME")
DATABASE = os.getenv("DATABASE_RESOURCE")
SCHEMA = os.getenv("SCHEMA_RESOURCE")
TABLE = os.getenv("TABLE_RESOURCE")

class RedisService:

    def __init__(self):
        self.__redis_host = os.getenv("REDIS_HOST")
        self.__redis_port = os.getenv("REDIS_PORT")
        self.__redis_key = os.getenv("REDIS_ENDPOINT_KEY")
        self.__redis = self.connect()

    def connect(self):
        try:
            return Redis(host=self.__redis_host, port=self.__redis_port, db=0)
        except Exception as exc:
            log.error(
                f"[Endpoint_1 - REDIS] Could not connect to Redis with "
                f"REDIS_HOST: {str(self.__redis_host)}" 
                f"REDIS_PORT: {str(self.__redis_port)}"
            )
            raise exc

    def get_value(self, key):
        log.info(f"[REDIS] Getting key: {key}")
        result = self.__redis.get(key)
        if result:
            result = result.decode('utf8').replace("'", '"')
            return json.loads(result)
        return None

    def set_value(self, key, value):
        log.info(f"[REDIS] Setting key: {key}")
        # return self.__redis.set(key, value, ex=REDIS_EXPIRATION_TIME)
        return self.__redis.set(key, value)

    def delete_value(self, key):
        log.info(f"[REDIS] Deleting key: {key}")
        self.__redis.delete(key)

    def save_execution_info(self, start_id, last_id , status_process):
        redis_payload = self.create_redis_payload(start_id, last_id, status_process)
        self.set_value(self.__redis_key, redis_payload)

    def get_execution_info(self):
        return self.get_value(self.__redis_key)

    def create_redis_payload(self, start_id, last_id, status):
        payload = {
            'database_resource': DATABASE,
            'schema_resource': SCHEMA,
            'table_resource': TABLE,
            'start_date': str(datetime.now()),
            'start_id': start_id,
            'last_id': last_id,
            'status_process': status
        }
        return json.dumps(payload)
