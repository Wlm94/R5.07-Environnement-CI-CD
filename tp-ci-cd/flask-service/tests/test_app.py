import pytest
import json
import os
from app import app, init_db, get_db_connection
from models import Product

@pytest.fixture
def client(tmp_path):
    os.environ['TESTING'] = 'True'
    app.config['TESTING'] = True

    # Base SQLite temporaire (ex: /tmp/test.db)
    app.config['TEST_DB_PATH'] = str(tmp_path / "test.db")

    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client

    
    # Nettoie après les tests
    connection = get_db_connection()
    if connection:
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM products')
            connection.commit()
        except Exception as e:
            print(f"Cleanup error: {e}")
        finally:
            if cursor:
                cursor.close()
            # NE PAS FERMER LA CONNEXION en mode test!

def test_create_product(client):
    """Test la création d'un produit"""
    # Données de test
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'description': 'Test description'
    }
    
    # Envoi de la requête
    response = client.post('/api/products', 
                         data=json.dumps(product_data),
                         content_type='application/json')
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    
    # Vérifications
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Product'
    assert data['price'] == 29.99
    assert 'id' in data

def test_get_products_empty(client):
    """Test la récupération de produits (liste vide)"""
    response = client.get('/api/products')
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_get_products_with_data(client):
    """Test la récupération de produits (avec données)"""
    # Crée d'abord un produit
    product_data = {
        'name': 'Test Product',
        'price': 29.99
    }
    response = client.post('/api/products', 
               data=json.dumps(product_data),
               content_type='application/json')
    assert response.status_code == 201
    
    # Récupère les produits
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Product'

def test_get_product_by_id(client):
    """Test la récupération d'un produit par ID"""
    # Crée un produit
    product_data = {
        'name': 'Test Product',
        'price': 29.99
    }
    create_response = client.post('/api/products', 
                                data=json.dumps(product_data),
                                content_type='application/json')
    assert create_response.status_code == 201
    product_id = json.loads(create_response.data)['id']
    
    # Récupère le produit par ID
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Product'

def test_get_nonexistent_product(client):
    """Test la récupération d'un produit inexistant"""
    response = client.get('/api/products/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_create_product_missing_fields(client):
    """Test la création avec des champs manquants"""
    # Sans nom
    product_data = {'price': 29.99}
    response = client.post('/api/products', 
                         data=json.dumps(product_data),
                         content_type='application/json')
    assert response.status_code == 400
    
    # Sans prix
    product_data = {'name': 'Test Product'}
    response = client.post('/api/products', 
                         data=json.dumps(product_data),
                         content_type='application/json')
    assert response.status_code == 400

def test_product_model():
    """Test le modèle Product"""
    product = Product(1, 'Test Product', 29.99, 'Test description')
    assert product.id == 1
    assert product.name == 'Test Product'
    assert product.price == 29.99
    
    # Test la conversion en dictionnaire
    product_dict = product.to_dict()
    assert product_dict['id'] == 1
    assert product_dict['name'] == 'Test Product'