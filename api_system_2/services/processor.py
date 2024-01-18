import os
from structlog import get_logger
from api_system_2.services.redis import RedisService
from api_system_2.services.order import OrderService

log = get_logger()
redis_service = RedisService()
order_service = OrderService()

FINISHED_PROCESS = os.getenv('FINISHED_PROCESS_INFO')
ERROR_PROCESS = os.getenv('ERROR_PROCESS_INFO')

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
                last_id = execution_info.get('last_id')
        else:
            last_id = 0
        self.run(last_id)

    def run(self, last_id):
        success, last_id = order_service.send_orders_to_queue(last_id)
        if success:
            log.info("[PROCESSOR] processed OK")
            redis_service.save_execution_info(last_id, FINISHED_PROCESS)
        else:
            redis_service.save_execution_info(last_id, ERROR_PROCESS)

    def clear(self):
        redis_service.clear_execution_info()

    def unblock(self):
        redis_service.unblock_execution_info()
