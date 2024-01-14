import sys
sys.path.append("..")

import os
import pika

from structlog import get_logger
from services.historic import HistoricService
from services.rabbitmq import RabbitmqConsumer

historic = HistoricService()
log = get_logger()


def back_to_queue(channel, method, attempts, body):
    log.info("[CONSUMER - RabbitMQ] Sending back to queue...")
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
        log.info("[CONSUMER - ok] Ready to process...")
        historic.save(body)
        back_to_queue(ch, method, retries, body)
    else:
        log.warning("[CONSUMER - exceed attempts] Sending to DLQ...")
        ch.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=False)


rabitmq_consumer = RabbitmqConsumer(process_message)
rabitmq_consumer.start()
