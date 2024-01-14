import os
from structlog import get_logger
from api_system_2.services.redis import RedisService
from api_system_2.services.order import OrderService

log = get_logger()
redis_service = RedisService()
order_service = OrderService()

FINISHED_PROCESS = 'FINISHED'
ERROR_PROCESS = 'ERROR'

class ProcessorService:

    def __init__(self):
        pass

    def start(self):
        execution_info = redis_service.get_execution_info()
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
            redis_service.save_execution_info(start_id, last_id, FINISHED_PROCESS)
        else:
            return redis_service.save_execution_info(start_id, last_id, ERROR_PROCESS)
