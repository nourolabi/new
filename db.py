
import sqlite3

DATABASE_NAME = 'glanzwerk.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kfz TEXT NOT NULL UNIQUE,
            tel TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            standard_price REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nr TEXT NOT NULL UNIQUE,
            date TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            rabatt REAL NOT NULL DEFAULT 0.0,
            mwst REAL NOT NULL,
            total REAL NOT NULL,
            zahlart TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            qty REAL NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def insert_customer(name, kfz, tel=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO customers (name, kfz, tel) VALUES (?, ?, ?)', (name, kfz, tel))
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id

def get_customer_by_kfz(kfz):
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM customers WHERE kfz = ?', (kfz,)).fetchone()
    conn.close()
    return customer

def get_all_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return customers

def insert_service(name, standard_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO services (name, standard_price) VALUES (?, ?)', (name, standard_price))
    conn.commit()
    service_id = cursor.lastrowid
    conn.close()
    return service_id

def get_all_services():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services').fetchall()
    conn.close()
    return services

def get_service_by_name(name):
    conn = get_db_connection()
    service = conn.execute('SELECT * FROM services WHERE name = ?', (name,)).fetchone()
    conn.close()
    return service

def update_service(service_id, name, standard_price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE services SET name = ?, standard_price = ? WHERE id = ?', (name, standard_price, service_id))
    conn.commit()
    conn.close()

def delete_service(service_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()

def insert_invoice(nr, date, customer_id, subtotal, rabatt, mwst, total, zahlart):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO invoices (nr, date, customer_id, subtotal, rabatt, mwst, total, zahlart) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (nr, date, customer_id, subtotal, rabatt, mwst, total, zahlart))
    conn.commit()
    invoice_id = cursor.lastrowid
    conn.close()
    return invoice_id

def get_latest_invoice_number():
    conn = get_db_connection()
    invoice = conn.execute('SELECT nr FROM invoices ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    if invoice:
        return invoice['nr']
    return None

def insert_invoice_item(invoice_id, service_name, qty, unit_price, line_total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO invoice_items (invoice_id, service_name, qty, unit_price, line_total) VALUES (?, ?, ?, ?, ?)',
                   (invoice_id, service_name, qty, unit_price, line_total))
    conn.commit()
    conn.close()

def get_invoice_details(invoice_id):
    conn = get_db_connection()
    invoice = conn.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,)).fetchone()
    items = conn.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,)).fetchall()
    conn.close()
    return invoice, items

def get_invoices_by_customer(customer_id):
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoices WHERE customer_id = ? ORDER BY date DESC', (customer_id,)).fetchall()
    conn.close()
    return invoices


if __name__ == '__main__':
    init_db()
    print("Database initialized and tables created.")
    # Example usage:
    # insert_service("Außenreinigung per Hand", 25.00)
    # insert_service("Felgenreinigung & Flugrostentfernung", 35.00)
    # print(get_all_services())





# Add new services
def add_initial_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    services_to_add = [
        ("Außenreinigung per Hand", 25.00),
        ("Felgenreinigung & Flugrostentfernung", 35.00),
        ("Innenraumreinigung", 40.00),
        ("Lederreinigung & -pflege", 50.00),
        ("Lederreparatur", 100.00),
        ("Polster- & Teppichreinigung", 60.00),
        ("Scheibenreinigung innen & außen", 15.00),
        ("Lackpolitur & Glanzversiegelung", 150.00),
        ("Nano-Keramik-Versiegelung", 300.00),
        ("Motorraumreinigung", 30.00),
        ("Geruchsneutralisierung & Ozonbehandlung", 70.00),
        ("Tierhaarentfernung", 45.00),
        ("Hagelschaden- und Dellenentfernung (Ausbeulen ohne Lackieren)", 200.00),
        ("Auto Folieren", 500.00),
        ("Abhol- und Bringservice", 20.00)
    ]
    for service_name, price in services_to_add:
        try:
            cursor.execute("INSERT INTO services (name, standard_price) VALUES (?, ?)", (service_name, price))
        except sqlite3.IntegrityError:
            # Service already exists, skip
            pass
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    add_initial_services()
    print("Database initialized and initial services added.")


