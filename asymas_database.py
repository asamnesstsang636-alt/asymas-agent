import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('asymas.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix_achat REAL,
            prix_vente REAL,
            stock INTEGER,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('asymas.db')
    df = pd.read_sql_query("SELECT * FROM inventaire", conn)
    conn.close()
    return df

def add_product(nom, prix_achat, prix_vente, stock, description):
    conn = sqlite3.connect('asymas.db')
    conn.execute("INSERT INTO inventaire (nom, prix_achat, prix_vente, stock, description) VALUES (?, ?, ?, ?, ?)", 
                 (nom, prix_achat, prix_vente, stock, description))
    conn.commit()
    conn.close()

def delete_product(id):
    conn = sqlite3.connect('asymas.db')
    conn.execute("DELETE FROM inventaire WHERE id = ?", (id,))
    conn.commit()
    conn.close()
