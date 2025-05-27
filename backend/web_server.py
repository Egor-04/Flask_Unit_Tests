import psycopg2
import requests
from flask import Flask, jsonify, request, render_template
from psycopg2.extras import RealDictCursor
from werkzeug.utils import redirect
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
users = {'Admin': 'admin_password', 'User': 'user_password'}

def connect_to_db():
    conn = psycopg2.connect(database='Employee_DataBase', user='administrator', password='root', host='localhost',
                            port='5432')
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            return f'Вы успешно вошли на сайт!'
        else: return 'Неверное имя пользователя или пароль!', 401

    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/employees', methods=['POST'])
def add_employee():
    """
    Add a new employee to the database
    ---
    tags:
      - Employees
    parameters:
      - in: body
        name: body
        schema:
          id: Employee
          required:
            - name
            - position
          properties:
            name:
              type: string
              description: Name of the employee
            position:
              type: string
              description: Job position of the employee
    responses:
      201:
        description: Employee created successfully
        schema:
          id: EmployeeResponse
          properties:
            id:
              type: integer
              description: The ID of the created employee
            name:
              type: string
            position:
              type: string
      400:
        description: Invalid input
    """
    data = request.get_json()
    name = data.get('name')
    position = data.get('position')

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Employee (name, position) VALUES (%s, %s) RETURNING employee_id', (name, position))
    employee_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'id': employee_id, 'name': name, 'position': position}), 201


@app.route('/employees', methods=['GET'])
def get_employees_list():
    """
    Get list of all employees
    ---
    tags:
      - Employees
    responses:
      200:
        description: A list of employees
        schema:
          type: array
          items:
            $ref: '#/definitions/EmployeeResponse'
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT employee_id, name, position FROM Employee')
    employees = cursor.fetchall()
    cursor.close()
    connection.close()

    employees_list = [{'id': emp[0], 'name': emp[1], 'position': emp[2]} for emp in employees]
    return jsonify(employees_list), 200


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """
    Get details of a specific employee
    ---
    tags:
      - Employees
    parameters:
      - name: employee_id
        in: path
        type: integer
        required: true
        description: Numeric ID of the employee to get
    responses:
      200:
        description: Employee details
        schema:
          $ref: '#/definitions/EmployeeResponse'
      404:
        description: Employee not found
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT employee_id, name, position FROM Employee WHERE employee_id = %s', (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    connection.close()

    if employee is None:
        return jsonify({'Error': 'Employee not found'}), 404

    return jsonify({'id': employee[0], 'name': employee[1], 'position': employee[2]}), 200


@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_info(employee_id):
    """
    Update employee information
    ---
    tags:
      - Employees
    parameters:
      - name: employee_id
        in: path
        type: integer
        required: true
        description: Numeric ID of the employee to update
      - in: body
        name: body
        schema:
          $ref: '#/definitions/Employee'
    responses:
      200:
        description: Employee updated successfully
        schema:
          $ref: '#/definitions/EmployeeResponse'
      404:
        description: Employee not found
      400:
        description: Invalid input
    """
    data = request.get_json()
    name = data.get('name')
    position = data.get('position')

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('UPDATE Employee SET name = %s, position = %s WHERE employee_id = %s RETURNING employee_id, name, position', (name, position, employee_id))
    updated_employee = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    if updated_employee:
        return jsonify({'id': updated_employee[0], 'name': updated_employee[1], 'position': updated_employee[2]}), 200
    else:
        return jsonify({'message': 'Employee not found'}), 404


@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """
    Delete an employee
    ---
    tags:
      - Employees
    parameters:
      - name: employee_id
        in: path
        type: integer
        required: true
        description: Numeric ID of the employee to delete
    responses:
      200:
        description: Employee deleted successfully
        schema:
          properties:
            message:
              type: string
              description: Success message
      404:
        description: Employee not found
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Employee WHERE employee_id = %s', (employee_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Employee deleted successfully'}), 200


def web_request():
    return requests.get("http://127.0.0.1:5000/employees")


if __name__ == '__main__':
    app.run(debug=True)