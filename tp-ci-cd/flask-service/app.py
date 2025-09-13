import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Product

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
if os.environ.get('TESTING') == 'True':
    # Utilise SQLite en mémoire pour les tests
    TEST_DB_PATH = app.config.get('TEST_DB_PATH', ':memory:')

    # Import pour SQLite
    from sqlite3 import Error
    # Connexion persistante pour les tests
    test_connection = None
else:
    # Configuration normale MySQL
    db_config = {
        'host': '192.168.1.48',
        'port': 3306,
        'database': 'productdb',
        'user': 'flaskuser',
        'password': 'flaskpass'
    }
    # Import pour MySQL
    from mysql.connector import Error

def get_db_connection():
    if os.environ.get('TESTING') == 'True':
        global test_connection
        if test_connection is None:
            # Crée une nouvelle connexion persistante
            test_connection = sqlite3.connect(TEST_DB_PATH)
            test_connection.row_factory = sqlite3.Row
        return test_connection
    else:
        # MySQL pour la production
        import mysql.connector
        try:
            connection = mysql.connector.connect(**db_config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

# Initialisation de la base de données
def init_db():
    connection = get_db_connection()
    if connection:
        cursor = None
        try:
            cursor = connection.cursor()
            # Utilise la syntaxe SQLite compatible
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()
            print("Database initialized successfully")
            
            # Vérification que la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            table_exists = cursor.fetchone()
            print(f"Table 'products' exists: {table_exists is not None}")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if cursor:
                cursor.close()
            # NE PAS FERMER LA CONNEXION en mode test!
            if os.environ.get('TESTING') != 'True':
                connection.close()

@app.route('/api/products', methods=['GET'])
def get_products():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = None
    try:
        if os.environ.get('TESTING') == 'True':
            cursor = connection.cursor()
        else:
            cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM products')
        
        if os.environ.get('TESTING') == 'True':
            # Conversion manuelle pour SQLite
            columns = [col[0] for col in cursor.description]
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            products = cursor.fetchall()
            
        return jsonify(products)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        # NE PAS FERMER LA CONNEXION en mode test!
        if os.environ.get('TESTING') != 'True':
            connection.close()

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Name and price are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = None
    try:
        cursor = connection.cursor()
        
        if os.environ.get('TESTING') == 'True':
            # SQLite syntax
            cursor.execute(
                'INSERT INTO products (name, price, description) VALUES (?, ?, ?)',
                (data['name'], data['price'], data.get('description', ''))
            )
        else:
            # MySQL syntax
            cursor.execute(
                'INSERT INTO products (name, price, description) VALUES (%s, %s, %s)',
                (data['name'], data['price'], data.get('description', ''))
            )
            
        connection.commit()
        
        product_id = cursor.lastrowid
        return jsonify({
            'id': product_id,
            'name': data['name'],
            'price': data['price'],
            'description': data.get('description', '')
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        # NE PAS FERMER LA CONNEXION en mode test!
        if os.environ.get('TESTING') != 'True':
            connection.close()

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = None
    try:
        if os.environ.get('TESTING') == 'True':
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                product = dict(zip(columns, row))
            else:
                product = None
        else:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
            product = cursor.fetchone()
        
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        # NE PAS FERMER LA CONNEXION en mode test!
        if os.environ.get('TESTING') != 'True':
            connection.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)