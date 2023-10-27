import pika
import json

def place_order(order_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    payload = json.dumps({
        'order_id': order_id,
        'status': 'new'
    })

    channel.basic_publish(exchange='',
                          routing_key='payment_queue',
                          body=payload)

    print(f"Sent order {order_id} to queue")
    connection.close()

if __name__ == "__main__":
    place_order("order_123")
