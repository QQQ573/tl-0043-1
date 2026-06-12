import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'devices.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE devices ADD COLUMN status VARCHAR(20) DEFAULT "在库待售"')
    conn.commit()
    print('Added status column to devices table')
except Exception as e:
    print(f'Status column: {e}')

try:
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)')
    conn.commit()
    print('Added status index')
except Exception as e:
    print(f'Status index: {e}')

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        device_id INTEGER NOT NULL,
        trade_type VARCHAR(20) NOT NULL,
        actual_amount FLOAT NOT NULL,
        counterparty_name VARCHAR(100) NOT NULL,
        trade_date DATE NOT NULL,
        settlement_method VARCHAR(20) NOT NULL,
        notes TEXT,
        is_deleted BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        deleted_at DATETIME,
        created_by VARCHAR(50),
        updated_by VARCHAR(50),
        deleted_by VARCHAR(50),
        FOREIGN KEY (device_id) REFERENCES devices (id)
    )
    """)
    conn.commit()
    print('Created transactions table')
except Exception as e:
    print(f'Transactions table: {e}')

try:
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_device_id ON transactions(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_trade_type ON transactions(trade_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_trade_date ON transactions(trade_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_is_deleted ON transactions(is_deleted)')
    conn.commit()
    print('Created transactions indexes')
except Exception as e:
    print(f'Transactions indexes: {e}')

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'\nTables in database: {[t[0] for t in tables]}')

cursor.execute("PRAGMA table_info(devices)")
cols = cursor.fetchall()
print(f'\nDevices columns: {[c[1] for c in cols]}')

cursor.execute("PRAGMA table_info(transactions)")
cols = cursor.fetchall()
print(f'Transactions columns: {[c[1] for c in cols]}')

conn.close()
print('\nMigration complete!')
