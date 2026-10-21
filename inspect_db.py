import sqlite3
import pandas as pd

conn = sqlite3.connect('data/processed/retail_bi.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', c.fetchall())
c.execute('PRAGMA table_info(customer_transactions)')
print('Schema:', c.fetchall())
c.execute('SELECT COUNT(*) FROM customer_transactions')
print('Row count:', c.fetchone())
conn.close()
