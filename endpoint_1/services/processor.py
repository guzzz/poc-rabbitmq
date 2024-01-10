import os
import json

from datetime import datetime
from structlog import get_logger
from endpoint_1.services.redis import RedisService

log = get_logger()
redis = RedisService()

RUNNING_PROCESS = 'RUNNING'
FINISHED_PROCESS = 'FINISHED'
ERROR_PROCESS = 'ERROR'

class ProcessorService:

    def __init__(self):
        self.__database = os.getenv("DATABASE_RESOURCE")
        self.__schema = os.getenv("SCHEMA_RESOURCE")
        self.__table = os.getenv("TABLE_RESOURCE")
        self.__redis_key = os.getenv("REDIS_ENDPOINT_KEY")

    def create_payload(self, start_id, status):
        payload = {
            'database_resource': self.__database,
            'schema_resource': self.__schema,
            'table_resource': self.__table,
            'start_date': str(datetime.now()),
            'start_id': start_id,
            'status_process': status
        }
        return json.dumps(payload)

    def run(self):
        result = redis.get_value(self.__redis_key)
        if result:
            result = result.decode('utf8').replace("'", '"')
            data = json.loads(result)
            if data.get("status_process", True) == 'FINISHED':
                start_id = data.get('start_id', 0) + 1 
                status_process = RUNNING_PROCESS
                payload = self.create_payload(start_id, status_process)
                redis.set_value(self.__redis_key, payload)
            else:
                self.error_message()
        else:
            start_id = 1 
            status_process = RUNNING_PROCESS
            payload = self.create_payload(start_id, status_process)
            redis.set_value(self.__redis_key, payload)

    def finish(self):
        result = redis.get_value(self.__redis_key)
        if result:
            result = result.decode('utf8').replace("'", '"')
            data = json.loads(result)
            if data.get('status_process', True) == 'RUNNING':
                payload = self.create_payload(result.get('start_id'), FINISHED_PROCESS)
                redis.set_value(self.__redis_key, payload)
                return
        self.error_message()

    def error(self):
        result = redis.get_value(self.__redis_key)
        if result:
            result = result.decode('utf8').replace("'", '"')
            data = json.loads(result)
            if data.get('status_process', True) == 'RUNNING':
                payload = self.create_payload(result.get('start_id'), ERROR_PROCESS)
                redis.set_value(self.__redis_key, payload)
                return
        self.error_message()

    def error_message(self):
        log.error(f"[ERROR] Impossible to process")