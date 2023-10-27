import pika
import json
import random

def simulate_api_call():
    return random.choice([True, False])

def initiate_shipping(ch, method, properties, body):
    payload = json.loads(body)
    order_id = payload['order_id']
    history = payload.get('history', [])

    if simulate_api_call():
        next_queues = []
        payload['status'] = 'shipping_done'
        print(f"Shipping initiated for {order_id}")
    else:
        payload['status'] = 'shipping_failed'
        next_queues = history
        print(f"Shipping failed for {order_id}")

    for next_queue in next_queues :
        ch.basic_publish(exchange='',
                        routing_key=next_queue,
                        body=json.dumps(payload))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def handle_rollback(ch, method, properties, body):
    payload = json.loads(body)
    print(f"Shipping rollback logic here for {payload['order_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_consume(queue='shipping_queue', on_message_callback=initiate_shipping)
    channel.basic_consume(queue='shipping_rollback_queue', on_message_callback=handle_rollback)

    print('Shipping Service waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
