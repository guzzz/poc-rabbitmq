import sys
sys.path.append("..")

import os
import pika

from structlog import get_logger
from services.processor import ProcessorService
from services.rabbitmq import RabbitmqConsumer
from models import order
from config.postgresdb import engine

order.Base.metadata.create_all(bind=engine)

processor = ProcessorService()
log = get_logger()


def back_to_queue(channel, method, attempts, body):
    channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
    channel.basic_publish(
        exchange= os.getenv('RABBITMQ_EXCHANGE'),
        routing_key=os.getenv('RABBITMQ_ROUTING_KEY'),
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={
                'x-retry': attempts+1,
                'x-retry-limit': int(os.getenv('RABBITMQ_RETRY_LIMIT')),
                'x-delay': int(os.getenv('RABBITMQ_DELAY'))
            }
        )
    )

def process_message(ch, method, properties, body):
    retries = properties.headers.get('x-retry')
    retry_limit = properties.headers.get('x-retry-limit')
    if retries < retry_limit:
        log.info("[CONSUMER - valid] Ready to process...")

        success, should_send_to_dlq, message = processor.start(body)
        if success:
             log.info("[CONSUMER - success] Processed successfully!")
             ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
        else:
            if should_send_to_dlq:
                log.warning("[CONSUMER - fail on last attempt] Sending to DLQ...")
                ch.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=False)
            else:
                log.info("[CONSUMER - back] Sending back to queue...")
                back_to_queue(ch, method, retries, message)
    else:
        log.warning("[CONSUMER - invalid] Message attempts exceed max allowed. Sending to DLQ...")
        ch.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=False)


rabitmq_consumer = RabbitmqConsumer(process_message)
rabitmq_consumer.start()
