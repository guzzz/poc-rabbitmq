
import json
import os
import uuid
import random

from structlog import get_logger
from fastapi.encoders import jsonable_encoder

from api_system_1.repositories.orders import OrderRepository
from api_system_1.services.publisher import RabbitmqPublisher

log = get_logger()


class OrderService:
    
    def __init__(self):
        self.__repo  = OrderRepository()
        self.__publisher = RabbitmqPublisher()

        self.__system_name = os.getenv("SYSTEM_NAME")
        self.__database = os.getenv("DATABASE_RESOURCE")
        self.__schema = os.getenv("SCHEMA_RESOURCE")
        self.__table = os.getenv("TABLE_RESOURCE")
    
    def send_orders_to_queue(self, last_id_processed):
        orders, last_id = self.__repo.list(last_id_processed)
        for order in orders:
            order_json = jsonable_encoder(order)
            message = self.create_message(order_json)
            sent_to_queue = self.send_to_queue(message)
            if not sent_to_queue:
                return False, last_id
        return True, last_id

    def create_message(self, order):
        message = {
            'message_id': str(uuid.uuid4()),
            'processing': {
                'processing_attempts': 0,
                'processing_info': '',
                'processing_times': self.generate_processing_times(order.get('security_check')),
            },
            'origin': {
                'system': self.__system_name,
                'database_resource': self.__database,
                'schema_resource': self.__schema,
                'table_resource': self.__table,
            },
            'order': order,
        }
        return json.dumps(message)

    def send_to_queue(self, message):        
        try:
            log.info("[PROCESSOR - RabbitMQ] Sending message to queue...")
            self.__publisher.send_message(message)
            return True
        except:
            log.error("[PROCESSOR - RabbitMQ] Publisher fail...")
            return False
        
    def generate_processing_times(self, should_process):
        if should_process:
            return random.randint(1, 5)
        else:
            return 6
