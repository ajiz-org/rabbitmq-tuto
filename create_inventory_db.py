import sqlite3

connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    product_id TEXT PRIMARY KEY,
    quantity INTEGER
);
""")

cursor.execute("INSERT INTO inventory (product_id, quantity) VALUES ('item_1', 10)")

connection.commit()
connection.close()
