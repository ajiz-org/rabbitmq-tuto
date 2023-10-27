import sqlite3
import random
import time

class TransactionRollback(Exception):
    pass

class RollbackManager:
    def __init__(self):
        self.rollback_tasks = []

    def add_rollback(self, task):
        self.rollback_tasks.append(task)

    def rollback(self):
        for task in reversed(self.rollback_tasks):
            task()

def simulate_api_call(service_name):
    if random.choice([True, False]):
        print(f"{service_name} API call succeeded")
        return True
    else:
        print(f"{service_name} API call failed")
        return False

def check_inventory(order_id):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT quantity FROM inventory WHERE product_id='item_1'")
    result = cursor.fetchone()
    if result and result[0] > 0:
        return True
    else:
        raise TransactionRollback(f"Inventory check failed for {order_id}")

def update_inventory(order_id, rollback_manager):
    def rollback():
        print(f"Rolling back inventory update for {order_id}")
        cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE product_id='item_1'")
        connection.commit()

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE product_id='item_1'")
    connection.commit()
    rollback_manager.add_rollback(rollback)
    print(f"Updated inventory for {order_id}")

def process_payment(order_id, rollback_manager):
    def rollback():
        print(f"Refunding payment for {order_id}")

    if simulate_api_call("Payment Service"):
        rollback_manager.add_rollback(rollback)
        print(f"Processed payment for {order_id}")
    else:
        raise TransactionRollback(f"Payment processing failed for {order_id}")

def initiate_shipping(order_id, rollback_manager):
    if simulate_api_call("Shipping Service"):
        print(f"Initiated shipping for {order_id}")
    else:
        raise TransactionRollback(f"Shipping initiation failed for {order_id}")

def place_order(order_id):
    rollback_manager = RollbackManager()
    try:
        check_inventory(order_id)
        process_payment(order_id, rollback_manager)
        update_inventory(order_id, rollback_manager)
        initiate_shipping(order_id, rollback_manager)
        print(f"Successfully processed {order_id}")
    except TransactionRollback as e:
        print(e)
        rollback_manager.rollback()

if __name__ == "__main__":
    place_order("order_123")
