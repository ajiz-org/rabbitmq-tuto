import pika
import json
import random


def simulate_api_call():
    return random.choice([True, False])


def process_payment(ch, method, properties, body):
    payload = json.loads(body)
    order_id = payload["order_id"]
    history = payload.get("history", [])

    if simulate_api_call():
        history.append("payment_rollback_queue")
        next_queues = ["inventory_queue"]
        payload["history"] = history
        print(f"Processed payment for {order_id}")
    else:
        payload["status"] = "payment_failed"
        next_queues = history
        print(f"Payment failed for {order_id}")

    for next_queue in next_queues:
        ch.basic_publish(exchange="", routing_key=next_queue, body=json.dumps(payload))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def handle_rollback(ch, method, properties, body):
    payload = json.loads(body)
    print(f"Refunding {payload['order_id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.basic_consume(queue="payment_queue", on_message_callback=process_payment)
    channel.basic_consume(
        queue="payment_rollback_queue", on_message_callback=handle_rollback
    )

    print("Payment Service waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
