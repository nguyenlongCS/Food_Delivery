import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

sys.path.append('../backend')
from main import app


class FoodDeliveryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('main.get_db_connection')
    def test_register_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }

        response = self.app.post('/api/register',
                                 data=json.dumps(data),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    def test_register_password_mismatch(self, mock_db):
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'password123',
            'confirm_password': 'different'
        }

        response = self.app.post('/api/register',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertFalse(result['success'])
        self.assertIn('không khớp', result['message'])

    @patch('main.get_db_connection')
    def test_login_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'password123',
            'role': 'user'
        }

        data = {'username': 'testuser', 'password': 'password123'}
        response = self.app.post('/api/login',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertEqual(result['user']['username'], 'testuser')

    @patch('main.get_db_connection')
    def test_login_failure(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        data = {'username': 'wrong', 'password': 'wrong'}
        response = self.app.post('/api/login',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertFalse(result['success'])

    @patch('main.get_db_connection')
    def test_get_menu(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'Pizza',
                'price': 150000,
                'image': 'pizza.jpg',
                'description': 'Ngon'
            }
        ]

        response = self.app.get('/api/menu')
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['items'][0]['name'], 'Pizza')

    @patch('main.get_db_connection')
    def test_add_to_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        data = {'user_id': 1, 'item_id': 1, 'quantity': 2}
        response = self.app.post('/api/cart',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    def test_get_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'quantity': 2,
                'name': 'Pizza',
                'price': 150000,
                'image': 'pizza.jpg'
            }
        ]

        response = self.app.get('/api/cart/1')
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['items']), 1)

    @patch('main.get_db_connection')
    def test_update_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {'cart_id': 1, 'quantity': 3}
        response = self.app.put('/api/cart/update',
                                data=json.dumps(data),
                                content_type='application/json')

        result = json.loads(response.data)
        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    def test_remove_from_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.delete('/api/cart/1')
        result = json.loads(response.data)

        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    def test_create_order(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'item_id': 1,
                'quantity': 2,
                'price': 150000,
                'restaurant': 'Pizza House'
            }
        ]
        mock_cursor.lastrowid = 1

        data = {'user_id': 1}
        response = self.app.post('/api/order',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    def test_create_order_empty_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        data = {'user_id': 1}
        response = self.app.post('/api/order',
                                 data=json.dumps(data),
                                 content_type='application/json')

        result = json.loads(response.data)
        self.assertFalse(result['success'])
        self.assertIn('trống', result['message'])

    @patch('main.get_db_connection')
    def test_get_user_orders(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'restaurant': 'Pizza House',
                'total_amount': 180000,
                'status': 'pending',
                'created_at': '2025-01-01'
            }
        ]

        response = self.app.get('/api/orders/user/1')
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['orders']), 1)

    @patch('main.get_db_connection')
    def test_get_restaurant_orders(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'username': 'customer1',
                'total_amount': 180000,
                'status': 'pending',
                'created_at': '2025-01-01'
            }
        ]

        response = self.app.get('/api/orders/restaurant/Pizza%20House')
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertEqual(len(result['orders']), 1)

    @patch('main.get_db_connection')
    def test_update_order_status(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {'status': 'confirmed'}
        response = self.app.put('/api/orders/1/status',
                                data=json.dumps(data),
                                content_type='application/json')

        result = json.loads(response.data)
        self.assertTrue(result['success'])

    @patch('main.get_db_connection')
    @patch('main.secure_filename')
    def test_add_menu_item(self, mock_secure, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_secure.return_value = 'test.jpg'

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp.flush()

            with open(tmp.name, 'rb') as test_file:
                data = {
                    'name': 'Test Pizza',
                    'price': '200000',
                    'description': 'Delicious',
                    'category': 'pizza',
                    'delivery_time': '30',
                    'distance': '2.5',
                    'restaurant': 'Test Restaurant'
                }

                response = self.app.post('/api/menu',
                                         data=dict(data, image=test_file),
                                         content_type='multipart/form-data')

        os.unlink(tmp.name)
        result = json.loads(response.data)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()