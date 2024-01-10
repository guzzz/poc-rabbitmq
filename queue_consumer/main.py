import pika
import time
import os

class RabbitmqConsumer:
    def __init__(self, callback) -> None:
        self.__host = os.getenv('RABBITMQ_HOST')
        self.__port = os.getenv('RABBITMQ_PORT')
        self.__username = os.getenv('RABBITMQ_USER')
        self.__password = os.getenv('RABBITMQ_PWD')
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
            )
        )
        time.sleep(10)
        channel = pika.BlockingConnection(connection_parameters).channel()
        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )
        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=self.__callback
        )

        return channel
    
    def start(self):
        print(f'Listen RabbitMQ on Port {self.__port}')
        self.__channel.start_consuming()

def minha_callback(ch, method, properties, body):
    print(body)


rabitmq_consumer = RabbitmqConsumer(minha_callback)
rabitmq_consumer.start()
