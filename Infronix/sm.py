import sqlite3
import random

DB_PATH = "./Database.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create ESPNumber table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ESPNumber (
            ESPID INTEGER PRIMARY KEY AUTOINCREMENT,
            RFID INTEGER NOT NULL,
            TransactionAmt INTEGER,
            FOREIGN KEY (RFID) REFERENCES RFIDTable(RFID)
        )
    """)

    # Create RFIDTable table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RFIDTable (
            RFID INTEGER PRIMARY KEY,
            Balance INTEGER NOT NULL,
            ESPID INTEGER NOT NULL,
            "Transaction Amount" INTEGER,
            FOREIGN KEY (ESPID) REFERENCES ESPNumber(ESPID)
        )
    """)

    conn.commit()
    conn.close()

def insert_dummy_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generate 1000 unique RFID numbers
    rfid_numbers = [random.randint(1000, 9999) for _ in range(1000)]
    
    # Insert into RFIDTable
    for rfid in rfid_numbers:
        espid = random.randint(1, 500)  # Random ESPID
        balance = random.randint(100, 5000)  # Random balance
        transaction_amount = random.randint(10, 500)  # Random transaction amount
        cursor.execute("INSERT INTO RFIDTable (RFID, Balance, ESPID, \"Transaction Amount\") VALUES (?, ?, ?, ?)",
                       (rfid, balance, espid, transaction_amount))

    # Insert into ESPNumber (Multiple transactions per RFID)
    for _ in range(1000):
        espid = random.randint(1, 500)  # ESPID range
        rfid = random.choice(rfid_numbers)  # Pick an existing RFID
        transaction_amount = random.randint(10, 500)  # Random transaction
        cursor.execute("INSERT INTO ESPNumber (RFID, TransactionAmt) VALUES (?, ?)",
                       (rfid, transaction_amount))

    conn.commit()
    conn.close()

# Run the script
create_tables()
insert_dummy_data()

print("✅ 1000 dummy records inserted into both tables!")
