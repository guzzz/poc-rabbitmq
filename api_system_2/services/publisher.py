import pika
import time
import os


class RabbitmqPublisher:
    def __init__(self) -> None:
        self.__host = os.getenv('RABBITMQ_HOST')
        self.__port = os.getenv('RABBITMQ_PORT')
        self.__username = os.getenv('RABBITMQ_USER')
        self.__password = os.getenv('RABBITMQ_PWD')
        self.__exchange = os.getenv('RABBITMQ_EXCHANGE')
        self.__routing_key = os.getenv('RABBITMQ_ROUTING_KEY')
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
        return channel

    def send_message(self, body):
        self.__channel.basic_publish(
            exchange=self.__exchange,
            routing_key=self.__routing_key,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={
                    'x-retry': 0,
                    'x-retry-limit': int(os.getenv('RABBITMQ_RETRY_LIMIT')),
                    'x-delay': int(os.getenv('RABBITMQ_DELAY'))
                }
            )
        )
