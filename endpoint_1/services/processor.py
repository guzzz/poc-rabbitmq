import os
import json

from datetime import datetime
from structlog import get_logger
from endpoint_1.services.redis import RedisService
from endpoint_1.services.publisher import RabbitmqPublisher

log = get_logger()
redis = RedisService()
rabbitmq_publisher = RabbitmqPublisher()

RUNNING_PROCESS = 'RUNNING'
FINISHED_PROCESS = 'FINISHED'
ERROR_PROCESS = 'ERROR'

class ProcessorService:

    def __init__(self):
        self.__database = os.getenv("DATABASE_RESOURCE")
        self.__schema = os.getenv("SCHEMA_RESOURCE")
        self.__table = os.getenv("TABLE_RESOURCE")
        self.__redis_key = os.getenv("REDIS_ENDPOINT_KEY")

    def create_redis_payload(self, start_id, status):
        payload = {
            'database_resource': self.__database,
            'schema_resource': self.__schema,
            'table_resource': self.__table,
            'start_date': str(datetime.now()),
            'start_id': start_id,
            'status_process': status
        }
        return json.dumps(payload)
    
    def create_queue_payload(self):
        payload = {
            'database_resource': self.__database,
            'schema_resource': self.__schema,
            'table_resource': self.__table,
            'start_date': str(datetime.now()),
        }
        return json.dumps(payload) 
    
    def save_in_redis(self, start_id, status_process):
        redis_payload = self.create_redis_payload(start_id, status_process)
        redis.set_value(self.__redis_key, redis_payload)

    def start(self):
        result = redis.get_value(self.__redis_key)
        if result:            
            if result.get("status_process", True) == 'FINISHED':
                self.send_message(result.get('start_id', 0) + 1)
            else:
                self.error_message(result.get("status_process"))
        else:
            self.send_message(start_id=1)
            

    def run(self, start_id):
        result = redis.get_value(self.__redis_key)
        if result or start_id == 1:
            return self.save_in_redis(start_id, RUNNING_PROCESS)
        self.error_message(f"save: {RUNNING_PROCESS}")

    def finish(self):
        result = redis.get_value(self.__redis_key)
        if result:
            return self.save_in_redis(result.get('start_id'), FINISHED_PROCESS)
        self.error_message(f"save: {FINISHED_PROCESS}")

    def error(self):
        result = redis.get_value(self.__redis_key)
        if result:
            return self.save_in_redis(result.get('start_id'), ERROR_PROCESS)    
        self.error_message(f"save: {ERROR_PROCESS}")

    def error_message(self, location=None):
        log.error(f"[ERROR] Processor Service: {location}")

    def send_message(self, start_id):
        self.run(start_id)
        queue_payload = self.create_queue_payload()
        msg_sent_to_queue = self.send_to_queue(queue_payload)
        log.info(f'Message sent to queue: {msg_sent_to_queue}')
        if msg_sent_to_queue:
            self.finish()
        else:
            self.error_message("Preparing to send_message")

    def send_to_queue(self, payload):        
        try:
            rabbitmq_publisher.send_message(payload)
            return True
        except:
            self.error_message("RabbitMQ send_to_queue")
            return False
