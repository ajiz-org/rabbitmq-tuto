import pika
import json
import sqlite3

def handle_rollback(ch, method, properties, body):
    connection = sqlite3.connect("../inventory.db")
    cursor = connection.cursor()

    payload = json.loads(body)
    order_id = payload['order_id']
    status = payload['status']

    if status in ['payment_failed', 'inventory_failed', 'shipping_failed']:
        if status == 'inventory_failed' or status == 'shipping_failed':
            cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE product_id='item_1'")
            connection.commit()
            print(f"Inventory rollback done for {order_id}")

        print(f"Payment refunding (if needed) for {order_id}")

    print(f"Rollback complete for {order_id}")
    connection.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_consume(queue='rollback_queue', on_message_callback=handle_rollback)

    print('Rollback Service waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
