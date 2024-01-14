
import os
import pika
import time

from pika.exchange_type import ExchangeType


class RabbitmqConsumer:
    def __init__(self, callback) -> None:
        self.__host = os.getenv('RABBITMQ_HOST')
        self.__port = os.getenv('RABBITMQ_PORT')
        self.__username = os.getenv('RABBITMQ_USER')
        self.__password = os.getenv('RABBITMQ_PWD')
        self.__routing_key = os.getenv('RABBITMQ_ROUTING_KEY')
        self.__dlq_exchange = os.getenv('RABBITMQ_DLQ_EXCHANGE')
        self.__dlq_queue = os.getenv('RABBITMQ_DLQ_QUEUE')
        self.__exchange = os.getenv('RABBITMQ_EXCHANGE')
        self.__queue = os.getenv('RABBITMQ_QUEUE')
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            ),
            heartbeat=1800
        )
        time.sleep(10)
        channel = pika.BlockingConnection(connection_parameters).channel()

        channel.exchange_declare(
            exchange=self.__exchange,
            exchange_type='x-delayed-message',
            arguments={'x-delayed-type': 'direct'}
        )
        channel.exchange_declare(
            exchange=self.__dlq_exchange,
            exchange_type=ExchangeType.fanout
        )

        channel.queue_declare(
            queue=self.__queue, 
            arguments={ 'x-dead-letter-exchange': self.__dlq_exchange }
        )
        channel.queue_declare(self.__dlq_queue)

        channel.queue_bind(self.__queue, self.__exchange, self.__routing_key)
        channel.queue_bind(self.__dlq_queue, self.__dlq_exchange)
        
        channel.basic_consume(
            queue=self.__queue,
            on_message_callback=self.__callback
        )
        return channel
    
    def start(self):
        print(f'[CONSUMER - start] Listen RabbitMQ on Port {self.__port}')
        self.__channel.start_consuming()
