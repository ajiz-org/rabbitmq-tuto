import pika

def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare queues
    channel.queue_declare(queue='payment_queue')
    channel.queue_declare(queue='inventory_queue')
    channel.queue_declare(queue='shipping_queue')
    channel.queue_declare(queue='payment_rollback_queue')
    channel.queue_declare(queue='inventory_rollback_queue')
    channel.queue_declare(queue='shipping_rollback_queue')

    connection.close()

if __name__ == "__main__":
    setup_rabbitmq()
