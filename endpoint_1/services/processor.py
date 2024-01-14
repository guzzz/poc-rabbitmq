import os
from structlog import get_logger
from endpoint_1.services.redis import RedisService
from endpoint_1.services.order import OrderService

log = get_logger()
redis = RedisService()
order_service = OrderService()

FINISHED_PROCESS = 'FINISHED'
ERROR_PROCESS = 'ERROR'

class ProcessorService:

    def __init__(self):
        self.__database = os.getenv("DATABASE_RESOURCE")
        self.__schema = os.getenv("SCHEMA_RESOURCE")
        self.__table = os.getenv("TABLE_RESOURCE")

    def start(self):
        execution_info = redis.get_execution_info()
        if execution_info:            
            if execution_info.get("status_process") == ERROR_PROCESS:
                log.error(f"[PROCESSOR] Execution Status blocked")
                return
            else:
                start_id = execution_info.get('last_id')
        else:
            start_id = 0
        self.process(start_id)

    def process(self, start_id):
        success, last_id = order_service.send_orders_to_queue(start_id)
        if success:
            log.info("[PROCESSOR] processed OK")
            redis.save_execution_info(start_id, last_id, FINISHED_PROCESS)
        else:
            return redis.save_execution_info(start_id, last_id, ERROR_PROCESS)
