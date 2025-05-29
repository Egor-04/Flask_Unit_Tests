import json
from web_server import app, connect_to_db_as_admin
from unittest import TestCase


class Test(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.connection = connect_to_db_as_admin()
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
        DROP TABLE IF EXISTS Employee;

        CREATE TABLE IF NOT EXISTS Employee
        (
            employee_id SERIAL PRIMARY KEY,
            name VARCHAR,
            position VARCHAR
        );''')
        self.connection.commit()

    def tearDown(self):
        self.cursor.execute('DROP TABLE IF EXISTS Employee')
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def test_add_employees(self):
        response = self.app.post('/employees',
                                 data=json.dumps({'name': 'John Doe Test', 'position': 'Manager'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'id': 1, 'name': 'John Doe Test', 'position': 'Manager'})

    def test_get_employee(self):
        self.app.post('/employees', data=json.dumps({'name': 'Charlie Test', 'position': 'Developer'}),
                      content_type='application/json')

        response = self.app.get('/employees/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'id': 1, 'name': 'Charlie Test', 'position': 'Developer'})

    def test_update_employee(self):
        self.app.post('/employees', data=json.dumps({'name': 'David', 'position': 'Tester'}),
                      content_type='application/json')
        response = self.app.put('/employees/1',
                                data=json.dumps({'name': 'David Smith', 'position': 'QA Engineer'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'id': 1, 'name': 'David Smith', 'position': 'QA Engineer'})

    def test_delete_employee(self):
        self.app.post('/employees',
                      data=json.dumps({'name': 'Eve', 'position': 'Analyst'}),
                      content_type='application/json')
        response = self.app.delete('/employees/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Employee deleted successfully'})