import pika
import json
import sqlite3


def update_inventory(ch, method, properties, body):
    connection = sqlite3.connect("../inventory.db")
    cursor = connection.cursor()

    payload = json.loads(body)
    order_id = payload["order_id"]

    cursor.execute("SELECT quantity FROM inventory WHERE product_id='item_1'")
    result = cursor.fetchone()
    history = payload.get("history", [])

    if result and result[0] > 0:
        cursor.execute(
            "UPDATE inventory SET quantity = quantity - 1 WHERE product_id='item_1'"
        )
        connection.commit()
        history.append("inventory_rollback_queue")
        payload["status"] = "inventory_done"
        next_queues = ["shipping_queue"]
        payload["history"] = history
        print(f"Inventory updated for {order_id}")
    else:
        payload["status"] = "inventory_failed"
        next_queues = history
        print(f"Inventory update failed for {order_id}")

    connection.close()

    for next_queue in next_queues:
        ch.basic_publish(exchange="", routing_key=next_queue, body=json.dumps(payload))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def handle_rollback(ch, method, properties, body):
    connection = sqlite3.connect("../inventory.db")
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE inventory SET quantity = quantity + 1 WHERE product_id='item_1'"
    )
    connection.commit()
    connection.close()
    print(f"Inventory rolled back")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.basic_consume(queue="inventory_queue", on_message_callback=update_inventory)
    channel.basic_consume(
        queue="inventory_rollback_queue", on_message_callback=handle_rollback
    )

    print("Inventory Service waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
