
import json

from structlog import get_logger
from fastapi.encoders import jsonable_encoder
from services.historic import HistoricService

log = get_logger()

historic = HistoricService()


class ProcessorService:

    def __init__(self):
        pass

    def clean_message(self, message_in_bytes):
        message_json = jsonable_encoder(message_in_bytes)
        return json.loads(message_json)

    def start(self, message):
        message = self.clean_message(message)
        processing_info = message.get('processing')
        attempts = processing_info.get('processing_attempts') + 1
        processing_times = processing_info.get('processing_times') 
        if attempts == processing_times:
            return self.processed_successfully(message, attempts)
        elif attempts == 5 and attempts < processing_times:
            return self.should_cancel_process(message, attempts)
        else:
            return self.should_process_again(message, attempts)
        
    def save_process(self, message, attempt):
        message['processing']['processing_attempts'] = attempt
        historic.save(message)
        
    def processed_successfully(self, message, attempt):
        message['processing']['processing_info'] = f'SUCCESS at the {attempt} attempt.'
        self.save_process(message, attempt)
        success = True
        should_go_dlq = False
        return success, should_go_dlq, None

    def should_process_again(self, message, attempt):
        message['processing']['processing_info'] = f'It was not successful at the {attempt} attempt.'
        self.save_process(message, attempt)
        success = False
        should_go_dlq = False
        return success, should_go_dlq, self.convert_message_to_bytes(message)
    
    def should_cancel_process(self, message, attempt):
        message['processing']['processing_info'] = f'FAIL to process message - will send to DQL. Attempt: {attempt}/5'
        self.save_process(message, attempt)
        success = False
        should_go_dlq = True
        return success, should_go_dlq, self.convert_message_to_bytes(message)

    def convert_message_to_bytes(self, json_message):
        del json_message['_id']
        return json.dumps(json_message)
