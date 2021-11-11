import pika
from cti_receiver.business.executor import ProcessCommand

from cti_receiver.config import BROKER_HOST, BROKER_PORT, BROKER_USER, BROKER_PASSWORD
from cti_receiver.const import EXCHANGE_NAME, EXCHANGE_TYPE, QUEUE_NAME, AUTO_DELETE_QUEUE


def main():

    process = ProcessCommand()
    process.start()

    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=BROKER_HOST,
        port=int(BROKER_PORT),
        credentials=credentials)
    )

    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
    result = channel.queue_declare(queue=QUEUE_NAME, durable=False, auto_delete=AUTO_DELETE_QUEUE)
    channel.queue_bind(result.method.queue, exchange=EXCHANGE_NAME, routing_key='*.*.*.*.*')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=result.method.queue, on_message_callback=process.enqueue, auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    main()
