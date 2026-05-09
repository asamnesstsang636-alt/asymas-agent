import sqlite3
import pandas as pd

DB_NAME = 'asymas.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix_achat REAL,
            prix_vente REAL,
            stock INTEGER,
            description TEXT,
            type TEXT DEFAULT 'Article'
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            entreprise TEXT,
            resultat TEXT,
            montant_paye REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_inventaire():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM inventaire", conn)
    conn.close()
    return df

def get_clients():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df

def add_product(nom, prix_achat, prix_vente, stock, description, type_prod):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO inventaire (nom, prix_achat, prix_vente, stock, description, type) VALUES (?,?,?,?,?,?)",
                 (nom, prix_achat, prix_vente, stock, description, type_prod))
    conn.commit()
    conn.close()

def add_client(nom, entreprise, resultat, montant):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO clients (nom, entreprise, resultat, montant_paye) VALUES (?,?,?,?)",
                 (nom, entreprise, resultat, montant))
    conn.commit()
    conn.close()

def delete_item(table, id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(f"DELETE FROM {table} WHERE id =?", (id,))
    conn.commit()
    conn.close()
